from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
import model
import RewindClient

viz_obj = RewindClient.RewindClient()

class MyStrategy:
    TERRAIN_FROM_AREA = [RewindClient.AreaType.UNKNOWN, RewindClient.AreaType.FOREST, RewindClient.AreaType.SWAMP]
    WEATHER_FROM_AREA = [RewindClient.AreaType.UNKNOWN, RewindClient.AreaType.CLOUD, RewindClient.AreaType.RAIN]

    SIDE_FROM_ID = [RewindClient.Side.ALLY, RewindClient.Side.ENEMY]
    VEHICLE_FROM_TYPE = [RewindClient.UnitType.ARRV, RewindClient.UnitType.FIGHTER, RewindClient.UnitType.HELICOPTER, RewindClient.UnitType.IFV, RewindClient.UnitType.TANK]
    #Список целей для каждого типа техники, упорядоченных по убыванию урона по ним.
    preferredTargetTypesByVehicleType = dict()
    preferredTargetTypesByVehicleType[model.VehicleType.VehicleType.FIGHTER] = [
        model.VehicleType.VehicleType.HELICOPTER, 
        model.VehicleType.VehicleType.FIGHTER
    ]
    preferredTargetTypesByVehicleType[model.VehicleType.VehicleType.HELICOPTER] = [
        model.VehicleType.VehicleType.TANK,
        model.VehicleType.VehicleType.ARRV,
        model.VehicleType.VehicleType.HELICOPTER,
        model.VehicleType.VehicleType.IFV,
        model.VehicleType.VehicleType.FIGHTER
    ]
    preferredTargetTypesByVehicleType[model.VehicleType.VehicleType.IFV] = [
        model.VehicleType.VehicleType.HELICOPTER,
        model.VehicleType.VehicleType.ARRV,
        model.VehicleType.VehicleType.IFV,
        model.VehicleType.VehicleType.FIGHTER,
        model.VehicleType.VehicleType.TANK
    ]
    preferredTargetTypesByVehicleType[model.VehicleType.VehicleType.TANK] = [
        model.VehicleType.VehicleType.IFV,
        model.VehicleType.VehicleType.ARRV,
        model.VehicleType.VehicleType.TANK,
        model.VehicleType.VehicleType.FIGHTER,
        model.VehicleType.VehicleType.HELICOPTER
    ]

    terrainTypeByCellXY = 0
    weatherTypeByCellXY = 0
    vehicleById = dict()
    updateTickByVehicleId = dict()

    def move(self, me: Player, world: World, game: Game, move: Move):
        if world.tick_index == 0:
            self.initializeStrategy(world)
            move.action = ActionType.CLEAR_AND_SELECT
            move.right = world.width
            move.bottom = world.height
        if world.tick_index == 1:
            move.action = ActionType.MOVE
            move.x = world.width / 2.0
            move.y = world.height / 2.0
        
        
        self.initializeTick(me, world, game, move)
        viz_obj.end_frame()

    def initializeStrategy(self, world: World):
        self.terrainTypeByCellXY = world.terrain_by_cell_x_y
        self.weatherTypeByCellXY = world.weather_by_cell_x_y
        for i in range(32):
            for j in range(32): 
                if self.terrainTypeByCellXY[i][j]>0:
                    viz_obj.area_description(i, j, self.TERRAIN_FROM_AREA[self.terrainTypeByCellXY[i][j]])
                if self.weatherTypeByCellXY[i][j]>0:
                    viz_obj.area_description(i, j, self.WEATHER_FROM_AREA[self.weatherTypeByCellXY[i][j]])

    def initializeTick(self, me: Player, world: World, game: Game, move: Move):
        #self.me = me
        #self.world = world
        #self.game = game
        #self.mov = move

        for i in world.new_vehicles:
            self.vehicleById[i.id] = i
            self.updateTickByVehicleId[i.id] = world.tick_index
            viz_obj.living_unit(i.x, i.y, i.radius, i.durability, i.max_durability, i.remaining_attack_cooldown_ticks, i.attack_cooldown_ticks, i.selected, self.SIDE_FROM_ID[i.player_id-1],0, self.VEHICLE_FROM_TYPE[i.type])
            #viz_obj.message(str(i.player_id))
            

        for i in world.vehicle_updates:
            #vehicleId = i.id
            if i.durability == 0:
                self.vehicleById.pop(i.id)
                self.updateTickByVehicleId.pop(i.id)
            else:
                #viz_obj.message('in else upd ' + str(i.id))
                self.vehicleById[i.id].update(i)
                #viz_obj.message(' upd ' + str(i.id))
                self.updateTickByVehicleId[i.id] = world.tick_index
                viz_obj.living_unit(i.x, i.y, self.vehicleById[i.id].radius, i.durability, self.vehicleById[i.id].max_durability, i.remaining_attack_cooldown_ticks, self.vehicleById[i.id].attack_cooldown_ticks, i.selected, self.SIDE_FROM_ID[self.vehicleById[i.id].player_id-1],0, self.VEHICLE_FROM_TYPE[self.vehicleById[i.id].type])
                #viz_obj.message(' end ' + str(i.id))
    