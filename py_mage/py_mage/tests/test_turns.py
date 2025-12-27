from py_mage.core.game_state import GameState
from py_mage.core.player import Player
from py_mage.core.turn import Step


def test_turn_progression_cycles_steps():
    players = [Player("A"), Player("B")]
    game = GameState(players=players)
    start = game.turn_manager.current_step()
    for _ in range(len(Step)):
        game.advance_step()
    assert game.turn_manager.current_step() == start
