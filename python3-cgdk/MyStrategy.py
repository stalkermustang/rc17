from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
#import RewindClient

#viz_obj = RewindClient.RewindClient()
 
class MyStrategy:

    #


    def move(self, me: Player, world: World, game: Game, move: Move):
        
        def vizualize_init():
            wd = world.terrain_by_cell_x_y
            weat = world.weather_by_cell_x_y
            print (wd[0][0])
            for i in range(len(wd)):
                for k in range(len(wd[0])):
                    #viz_obj.area_description(i, k, wd[i][k])
                    viz_obj.area_description(i, k, weat[i][k])
                    #pass
            units = world.new_vehicles

            for i in units:
                print (i.player_id)
                viz_obj.living_unit(i.x, i.y, i.radius, i.durability, i.max_durability,  i.remaining_attack_cooldown_ticks, i.attack_cooldown_ticks, i.selected)

        def vizualize_upd():
            unit_upd = world.vehicle_updates
            for i in unit_upd:
                viz_obj.living_unit(i.x, i.y, 2, i.durability, 100)
            viz_obj.end_frame() 

        if world.tick_index == 0:
            #vizualize_init()
            move.action = ActionType.CLEAR_AND_SELECT
            move.left = world.width
            move.top = world.height


        if world.tick_index == 1:
            move.action = ActionType.MOVE
            move.x = world.width / 2.0
            move.y = world.height / 2.0

        #vizualize_upd()


