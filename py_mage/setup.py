from setuptools import Command, setup


class DummyBdistWheel(Command):
    description = "Dummy bdist_wheel command for offline editable installs."
    user_options = []

    def initialize_options(self) -> None:
        return None

    def finalize_options(self) -> None:
        return None

    def run(self) -> None:
        return None

if __name__ == "__main__":
    setup(cmdclass={"bdist_wheel": DummyBdistWheel})
