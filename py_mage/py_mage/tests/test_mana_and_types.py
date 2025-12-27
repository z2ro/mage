from py_mage.cards.mage_import import parse_types, validate_mana_cost


def test_validate_mana_cost_accepts_common_symbols():
    assert validate_mana_cost("{1}{G}{G}")
    assert validate_mana_cost("{X}{R}")
    assert validate_mana_cost("{2}{W/U}{B/P}")


def test_validate_mana_cost_rejects_invalid_symbols():
    assert not validate_mana_cost("{G}{?}")
    assert not validate_mana_cost("{G}{W")  # missing closing brace


def test_parse_types_extracts_card_types():
    content = "super(ownerId, setInfo, new CardType[]{CardType.CREATURE, CardType.ARTIFACT}, \"{2}\");"
    assert list(parse_types(content)) == ["CREATURE", "ARTIFACT"]
