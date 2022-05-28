import os,sys,json,enum,time
import numpy as np

sys.path.append("./general/")

class Place(enum.Enum):
    null = -2
    mountain = -1
    occupy_1 = 0
    occupy_2 = 1
    general_1 = 3
    general_2 = 4
    city_free = 5
    city_1 = 6
    city_2 = 7

class Color(enum.Enum):
    blac=30
    red=31
    green=32
    yellow=33
    blue=34
    magenta=35
    cyan_blue=36
    white=37

class G_game():
    '''
    user: 0,1 用于一些变量的索引
    width, height 地图尺寸
    geogra_map: -1为山
    users_map: 非城市的有士兵的地方
    armies_free_map: 未被任何人攻占过的城市
    armies_user_map: 被攻占下来的城市
    '''
    def __init__(self,size,cities,cityArmies,generals,mountains):
        # geogra_map 初始先设为-1，在后面再将有效部分设为0
        # belong_map :
        #  -2: free square
        #   0: user_1's square
        #   1: user_2's square
        #   3: user_1's general
        #   4: user_2's general
        #   5: free city
        #   6: user_1's city
        #   7: user_2's city
        self.width = size[0]
        self.height = size[1]
        self.cities = cities
        self.cityArmies = cityArmies
        self.gameover = [False, -1]
        self.generals = [
            self.coord_comp(generals[0]),
            self.coord_comp(generals[1]),
        ]
        self.mountains = mountains
        self.geogra_map = np.ones((25,25), np.int8)*-1
        self.users_map = np.zeros((2,25,25), )
        self.armies_free_map = np.zeros((25,25), )
        self.armies_user_map = np.zeros((2,25,25), )
        self.generals_map = np.zeros((2,25,25), np.int8)
        self.belong_map = np.ones((25,25),np.int8)*-2

    def coord_comp(self, place):
        y = int(place / self.width)
        x = place % self.width
        return (y,x)

    def init_work(self):
        # 将属于地图部分设为0
        for i in range(self.height):
            for j in range(self.width):
                self.geogra_map[i][j] = 0
        self.generals_map[0][self.generals[0]] = 1
        self.generals_map[1][self.generals[1]] = 1
        self.armies_user_map[0][self.generals[0]] = 1
        self.armies_user_map[1][self.generals[1]] = 1
        self.belong_map[self.generals[0]] = 3
        self.belong_map[self.generals[1]] = 4

        for mountain in self.mountains:
            self.geogra_map[(self.coord_comp(mountain))] = -1
        for index,army in enumerate(self.cities):
            coord = self.coord_comp(army)
            self.armies_free_map[coord] = self.cityArmies[index]*-1
            self.belong_map[coord] = 5

    def place_check(self,coord):
        if type(coord) == int: 
            coord = self.coord_comp(coord)
        if self.geogra_map[coord] == -1:
            return Place.mountain
        if self.belong_map[coord] == 6:
            return Place.city_1
        if self.belong_map[coord] == 7:
            return Place.city_2
        if self.belong_map[coord] == 5:
            return Place.city_free
        if self.belong_map[coord] == 3:
            return Place.general_1
        if self.belong_map[coord] == 4:
            return Place.general_2
        if self.belong_map[coord] == 0:
            return Place.occupy_1
        if self.belong_map[coord] == 1:
            return Place.occupy_2
        return Place.null

    def add_per_turn(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.belong_map[(i,j)] in \
                [Place.city_1.value, Place.general_1.value]:
                    self.armies_user_map[(0,i,j)] += 1
                elif self.belong_map[(i,j)] in \
                [Place.city_2.value, Place.general_2.value]:
                    self.armies_user_map[(1,i,j)] += 1

    def add_per_25turn(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.belong_map[(i,j)] == Place.occupy_1.value:
                    self.users_map[(0,i,j)] += 1
                if self.belong_map[(i,j)] in [Place.city_1.value, Place.general_1.value]:
                    self.armies_user_map[(0,i,j)] += 1
                if self.belong_map[(i,j)] == Place.occupy_2.value:
                    self.users_map[(1,i,j)] += 1
                if self.belong_map[(i,j)] in [Place.city_2.value, Place.general_2.value]:
                    self.armies_user_map[(1,i,j)] += 1

    def win(self, user: int):
        pass

    def move(self, info:list):
        [user, beg, end, half, turn] = info
        enemy = 1 - user
        beg = self.coord_comp(beg)
        end = self.coord_comp(end)
        beg_type = self.place_check(beg)
        end_type = self.place_check(end)
        if end_type == Place.mountain: return   # move to place of mountain

        half = (half==1)
        movenum,beg_place_num = -1,-1
        if beg_type.value == user:
            beg_place_num = int(self.users_map[user][beg])
        else:
            beg_place_num = int(self.armies_user_map[user][beg])
        if beg_place_num < 2: return

        if half:
            movenum = int(beg_place_num / 2)
        else: movenum = beg_place_num - 1
        if beg_type.value == user:
            self.users_map[user][beg] -= movenum
        else:
            self.armies_user_map[user][beg] -= movenum
        
        if (end_type.value in [Place.null.value, user]):
            # free square or user's square 
            self.belong_map[end] = user
            self.users_map[user][end] += movenum

        elif end_type.value == enemy:
            # enemy's square 
            enemy_num = int(self.users_map[enemy][end])
            num_gap = enemy_num - movenum
            if num_gap >= 0:
                self.users_map[enemy][end] = num_gap
            elif num_gap < 0:
                self.belong_map[end] = user
                self.users_map[enemy][end] = 0
                self.users_map[user][end] = num_gap*-1


        elif end_type == Place.city_free:
            # free city
            city_num = int(self.armies_free_map[end])
            num_gap = city_num + movenum
            if num_gap <= 0:
                self.armies_free_map[end] = num_gap
            elif num_gap > 0:
                self.belong_map[end] = 6+user
                self.armies_free_map[end] = 0
                self.armies_user_map[user][end] = num_gap

        elif end_type.value in [6+user,3+user]: 
            # user's city or general
            self.armies_user_map[user][end] += movenum

        elif end_type.value == 7-user: 
            # enemy's city
            city_num = int(self.armies_user_map[enemy][end])
            num_gap = city_num - movenum
            if num_gap >= 0:
                self.armies_user_map[enemy][end] = num_gap
            elif num_gap < 0:
                self.belong_map[end] = 6+user
                self.armies_user_map[user][end] = num_gap*-1
                self.armies_user_map[enemy][end] = 0


        elif end_type.value == 4-user: 
            # enemy's general
            city_num = int(self.armies_user_map[enemy][end])
            num_gap = city_num - movenum
            if num_gap >= 0:
                self.armies_user_map[enemy][end] = num_gap
            elif num_gap < 0:
                self.belong_map[end] = 3+user
                self.armies_user_map[user][end] = num_gap*-1
                self.armies_user_map[enemy][end] = 0
                self.gameover = [True,user]
                self.win(user)
                
