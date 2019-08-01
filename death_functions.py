from bearlibterminal import terminal

from game_states import GameStates

from render_functions import RenderOrder


def kill_player(player):
    player.char = '%'
    player.color = terminal.color_from_name('red')

    # return 'You died!', GameStates.PLAYER_DEAD
    return f'[color=red]You died![/color]', GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = '[color=orange]{0} is dead! Also this is a really really \nreally really really really really really long message to try and testing something.[/color]'.format(monster.name.capitalize())

    monster.char = '%'
    monster.color = terminal.color_from_name('red')
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message
