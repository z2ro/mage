from __future__ import annotations

import base64
import csv
import hashlib
import io
import os
import pathlib
import zipfile
from typing import Iterable, Optional

DIST_NAME = "py-mage"
NAME = "py_mage"
VERSION = "0.1.0"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"


def build_wheel(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    wheel_path = pathlib.Path(wheel_directory)
    wheel_path.mkdir(parents=True, exist_ok=True)
    filename = f"{NAME}-{VERSION}-py3-none-any.whl"
    archive_path = wheel_path / filename
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        _write_package_files(archive)
        record_rows = _write_dist_info(archive)
        _write_record(archive, record_rows)
    return filename


def build_editable(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    return build_wheel(wheel_directory, config_settings, metadata_directory)


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings=None) -> str:
    metadata_path = pathlib.Path(metadata_directory) / DIST_INFO
    metadata_path.mkdir(parents=True, exist_ok=True)
    (metadata_path / "METADATA").write_text(_metadata_contents(), encoding="utf-8")
    (metadata_path / "WHEEL").write_text(_wheel_contents(), encoding="utf-8")
    (metadata_path / "top_level.txt").write_text("py_mage\n", encoding="utf-8")
    return DIST_INFO


def _write_package_files(archive: zipfile.ZipFile) -> None:
    root = pathlib.Path(__file__).resolve().parent
    package_root = root / "py_mage"
    for path in package_root.rglob("*.py"):
        rel = path.relative_to(root)
        archive.write(path, str(rel))


def _write_dist_info(archive: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    record_rows: list[tuple[str, str, str]] = []
    files = {
        f"{DIST_INFO}/METADATA": _metadata_contents(),
        f"{DIST_INFO}/WHEEL": _wheel_contents(),
        f"{DIST_INFO}/top_level.txt": "py_mage\n",
    }
    for name, contents in files.items():
        archive.writestr(name, contents)
        record_rows.append(_record_row(name, contents))
    return record_rows


def _write_record(archive: zipfile.ZipFile, record_rows: Iterable[tuple[str, str, str]]) -> None:
    output = io.StringIO()
    writer = csv.writer(output)
    for row in record_rows:
        writer.writerow(row)
    writer.writerow([f"{DIST_INFO}/RECORD", "", ""])
    archive.writestr(f"{DIST_INFO}/RECORD", output.getvalue())


def _metadata_contents() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            f"Name: {DIST_NAME}",
            f"Version: {VERSION}",
            "Summary: Incremental Python migration of the MAGE rules engine",
            "Provides-Extra: dev",
            "Requires-Dist: pytest>=7; extra == 'dev'",
            "",
        ]
    )


def _wheel_contents() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: py_mage.build_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _record_row(path: str, contents: str) -> tuple[str, str, str]:
    digest = hashlib.sha256(contents.encode("utf-8")).digest()
    encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    size = str(len(contents.encode("utf-8")))
    return (path, f"sha256={encoded}", size)
