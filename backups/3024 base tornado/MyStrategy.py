from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
import model
import RewindClient
import numpy as np
from queue import Queue
import random

viz_obj = RewindClient.RewindClient()

class MyStrategy:
    TERRAIN_FROM_AREA = [RewindClient.AreaType.UNKNOWN, RewindClient.AreaType.FOREST, RewindClient.AreaType.SWAMP]
    WEATHER_FROM_AREA = [RewindClient.AreaType.UNKNOWN, RewindClient.AreaType.CLOUD, RewindClient.AreaType.RAIN]

    SIDE_FROM_ID = [RewindClient.Side.ALLY, RewindClient.Side.ENEMY]
    VEHICLE_FROM_TYPE = [RewindClient.UnitType.ARRV, RewindClient.UnitType.FIGHTER, RewindClient.UnitType.HELICOPTER, RewindClient.UnitType.IFV, RewindClient.UnitType.TANK]
    #Список целей для каждого типа техники, упорядоченных по убыванию урона по ним.
    preferredTargetTypesByVehicleType = {model.VehicleType.VehicleType.FIGHTER: [model.VehicleType.VehicleType.HELICOPTER, model.VehicleType.VehicleType.FIGHTER], model.VehicleType.VehicleType.HELICOPTER: [model.VehicleType.VehicleType.TANK, model.VehicleType.VehicleType.ARRV, model.VehicleType.VehicleType.HELICOPTER,  model.VehicleType.VehicleType.IFV, model.VehicleType.VehicleType.FIGHTER], model.VehicleType.VehicleType.IFV: [
        model.VehicleType.VehicleType.HELICOPTER,
        model.VehicleType.VehicleType.ARRV,
        model.VehicleType.VehicleType.IFV,
        model.VehicleType.VehicleType.FIGHTER,
        model.VehicleType.VehicleType.TANK
    ], model.VehicleType.VehicleType.TANK: [
        model.VehicleType.VehicleType.IFV,
        model.VehicleType.VehicleType.ARRV,
        model.VehicleType.VehicleType.TANK,
        model.VehicleType.VehicleType.FIGHTER,
        model.VehicleType.VehicleType.HELICOPTER
    ]}

    terrainTypeByCellXY = 0
    weatherTypeByCellXY = 0
    vehicleById = dict()
    updateTickByVehicleId = dict()
    delayedMoves = Queue()
    pointSOfFury = [[150, 350], [350, 150]]
    buildEnd = False

    def move(self, me: Player, world: World, game: Game, move: Move):
        self.preproc(world.tick_index, me, world, game, move)
        if me.remaining_action_cooldown_ticks > 0:
            viz_obj.end_frame()
            return
        
        if self.executeDelayedMove(move, world):
            viz_obj.end_frame()
            return
        
        self.baseBind(me, world, game, move)
        self.baseLogic(me, world, game, move)


        viz_obj.end_frame()

    def baseBind(self, me, world, game, move):
        if world.tick_index == 0:
            global group_counter
            group_counter =  1
            for i in ['TANK', 'IFV', 'ARRV', 'FIGHTER', 'HELICOPTER']:
                self.delayedMoves.put('move.action = model.ActionType.ActionType.CLEAR_AND_SELECT; \
                    move.right = world.width; move.bottom = world.height; move.vehicle_type = model.VehicleType.VehicleType.' + i)
                self.delayedMoves.put('move.action = model.ActionType.ActionType.ASSIGN; move.group = ' + str(group_counter))  
                
                group_counter+=1
            
            self.delayedMoves.put('move.action = model.ActionType.ActionType.CLEAR_AND_SELECT; move.group=1')
            self.delayedMoves.put('move.action = model.ActionType.ActionType.ADD_TO_SELECTION; move.group=2;')
            self.delayedMoves.put('move.action = model.ActionType.ActionType.ADD_TO_SELECTION; move.group=3;')
            self.delayedMoves.put('move.action = model.ActionType.ActionType.ADD_TO_SELECTION; move.group=4;')
            self.delayedMoves.put('move.action = model.ActionType.ActionType.ADD_TO_SELECTION; move.group=5;')
            for i in range(7):
                self.delayedMoves.put('move.action = model.ActionType.ActionType.ROTATE; x_c, y_c = self.getCenterOfSelected(); move.x = x_c; move.y = y_c; move.angle = '+str((i%2==0)*2-1)+'*1.5')
                for i in range(110):
                    self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.SCALE; x_c, y_c = self.getCenterOfSelected(); move.x = x_c; move.y = y_c; move.factor = 0.6')
                for i in range(30):
                    self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
            #self.delayedMoves.put('move.action = model.ActionType.ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height')
            #self.delayedMoves.put('move.action = model.ActionType.ActionType.SCALE; x_c, y_c = self.getCenterOfSelected(); move.x = x_c; move.y = y_c; move.factor = 3')
            self.delayedMoves.put('self.buildEnd = True; move.action = model.ActionType.ActionType.NONE')

    def baseLogic(self, me, world, game, move):
        if self.buildEnd:
            if world.tick_index % 150 == 0:
                viz_obj.message(str(world.tick_index)+' '+str(self.buildEnd))
                x_enemy_c, y_enemy_c = self.getCenterOfGroup(self.getEnemyVehicles(me))
                x_c, y_c = self.getCenterOfSelected()
                viz_obj.message(' '+str(x_enemy_c-x_c)+' '+str(y_enemy_c-y_c)+'\n')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.SCALE; x_c, y_c = self.getCenterOfSelected(); move.x = x_c; move.y = y_c; move.factor = 0.6')
                for i in range(20):
                    self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.ROTATE; x_c, y_c = self.getCenterOfSelected(); move.x = x_c; move.y = y_c; move.angle = 1.5')
                for i in range(55):
                    self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.MOVE; move.max_speed=0.3; move.x='+str(x_enemy_c-x_c)+'; move.y='+str(y_enemy_c-y_c))
        if me.remaining_nuclear_strike_cooldown_ticks == 0:
            x_enemy_c, y_enemy_c = self.getCenterOfGroup(self.getEnemyVehicles(me))
            x_c, y_c = self.getCenterOfSelected()
            viz_obj.message('ROCKET Potential! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
            nuc_veh_id = self.getNucaVehId(me)
            #viz_obj.message('ROCKET Potential! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
            viz_obj.message(str(nuc_veh_id))########
            if nuc_veh_id>0 and ((x_c-x_enemy_c)**2+(y_c-y_enemy_c)**2)**0.5 > 75:
                viz_obj.message('ROCKET GO! 11111111111111111111111111111111111111111111')
                viz_obj.message(str(nuc_veh_id))
                self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.NONE')
                self.delayedMoves.put('move.action = model.ActionType.ActionType.TACTICAL_NUCLEAR_STRIKE; move.x='+str(x_enemy_c)+'; move.y='+str(y_enemy_c)+'; move.vehicle_id='+str(nuc_veh_id))
                viz_obj.circle(x_enemy_c, y_enemy_c, 50, 0xFF0000)
                
                self.delayedMoves.put('move.action = model.ActionType.ActionType.MOVE; move.max_speed=0.3; move.x='+str(x_enemy_c-x_c)+'; move.y='+str(y_enemy_c-y_c))

    def getNucaVehId(self, me):
        my_veh = self.getMyVehicles(me)
        enemy_veh = self.getEnemyVehicles(me)
        x_enemy_c, y_enemy_c = self.getCenterOfGroup(enemy_veh)
        distances = []
        for i in my_veh:
            cur_dist = i.get_distance_to(x_enemy_c, y_enemy_c)
            if cur_dist<=80:
                distances.append([cur_dist, i.id])
        if len(distances)>17:
            distances.sort()
            return distances[10][1]
        else:
            return -1

    def executeDelayedMove(self, move: Move, world: World):
        if self.delayedMoves.empty():
            return False
        delayedMove = self.delayedMoves.get()
        exec(delayedMove)
        return True

    def preproc(self, tick_count, me: Player, world: World, game: Game, move: Move):
        if tick_count == 0:
            self.initializeStrategy(world)
        self.initializeTick(me, world, game, move)

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

        for i in world.new_vehicles:
            self.vehicleById[i.id] = i
            self.updateTickByVehicleId[i.id] = world.tick_index
            

        for i in world.vehicle_updates:
            if i.durability == 0:
                self.vehicleById.pop(i.id)
                self.updateTickByVehicleId.pop(i.id)
            else:
                self.vehicleById[i.id].update(i)
                self.updateTickByVehicleId[i.id] = world.tick_index

        for i in self.vehicleById.values():
            viz_obj.living_unit(i.x, i.y, i.radius, i.durability, i.max_durability, i.remaining_attack_cooldown_ticks, i.attack_cooldown_ticks, i.selected, self.SIDE_FROM_ID[i.player_id-1],0, self.VEHICLE_FROM_TYPE[i.type])
           
    def getVehiclesByGroupID(self, id):
        all_vehicles = []
        for i in self.vehicleById.values():
            if id in i.groups:
                all_vehicles.append(i)
        return all_vehicles

    def getCenterOfGroupByID(self, groupid):
        all_vehicles = self.getVehiclesByGroupID(groupid)
        return np.mean([i.x for i in all_vehicles]), np.mean([i.y for i in all_vehicles])

    def getCenterOfGroup(self, group):
        return np.mean([i.x for i in group]), np.mean([i.y for i in group])

    def getCenterOfGroupsByID(self, groups):
        viz_obj.message('HEY!\n')
        all_veh = []
        for i in self.vehicleById.values():
            if i.groups in groups:
                all_veh.append(i)
        viz_obj.message('HEY!\n')
        return np.mean([i.x for i in all_veh]), np.mean([i.y for i in all_veh])

    def getCenterOfSelected(self):
        selected_vehicles = [i for i in self.vehicleById.values() if i.selected==True]
        return np.mean([i.x for i in selected_vehicles]), np.mean([i.y for i in selected_vehicles])

    def getEnemyVehicles(self, me):
        return [i for i in self.vehicleById.values() if i.player_id!=me.id]

    def getMyVehicles(self, me):
        return [i for i in self.vehicleById.values() if i.player_id==me.id]
