from py_mage.cards.basic import (
    forest_definition,
    grizzly_bears_definition,
    lightning_bolt_definition,
    make_creature_spell,
    make_lightning_bolt_spell,
)
from py_mage.core.card import Card
from py_mage.core.game_state import GameState
from py_mage.core.player import Player


def test_cast_creature_resolves_to_battlefield():
    player = Player("A")
    player.library.cards.clear()
    forest = Card(forest_definition(), owner=player, controller=player)
    forest_two = Card(forest_definition(), owner=player, controller=player)
    bears = Card(grizzly_bears_definition(), owner=player, controller=player)
    player.battlefield.add(forest)
    player.battlefield.add(forest_two)
    player.hand.add(bears)

    game = GameState(players=[player])
    for land in (forest, forest_two):
        land_ability = land.definition.abilities[0](land, game)[0]
        land_ability.activate(game)
        game.pass_priority()

    game.cast_spell(player, bears, make_creature_spell(bears))
    game.pass_priority()

    assert bears in player.battlefield.cards


def test_lightning_bolt_kills_creature_with_sba():
    player = Player("A")
    opponent = Player("B")
    player.library.cards.clear()
    opponent.library.cards.clear()
    bears = Card(grizzly_bears_definition(), owner=opponent, controller=opponent)
    bolt = Card(lightning_bolt_definition(), owner=player, controller=player)
    opponent.battlefield.add(bears)
    player.hand.add(bolt)
    player.mana_pool.add("R", 1)

    game = GameState(players=[player, opponent])
    game.cast_spell(player, bolt, make_lightning_bolt_spell(bolt, bears))
    game.pass_priority()
    game.pass_priority()

    game.check_state_based_actions()

    assert bears in opponent.graveyard.cards
