import os,sys,json,enum,time
import numpy as np

# sys.path.append("./general/")

square_9 = [
    [
         1, 1, 1,
         0,    0,
        -1,-1,-1,
    ],[
        -1, 0, 1,
        -1,    1,
        -1, 0, 1,
    ]
]

square_4 = [
    [
            1,
         0,    0,
           -1,
    ],[
            0,
        -1,    1,
            0,
    ]
]

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

    def sum_army(self):
        num = [0,0,0,0]
        for i1 in [0,1]:
            for i in range(25):
                num[i1] += np.sum(self.users_map[i1][i])
                num[i1] += np.sum(self.armies_user_map[i1][i])

                island = np.int32(self.users_map[i1][i] + self.armies_user_map[i1][i]) > np.zeros((1,25))
                lands = np.sum(island)
                if lands > 0:
                    num[i1+2] += lands
        return num

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


        

    def maskL1(self, user: int):
        if user not in [0,1]:
            raise "Parameter Error: user<{}>".format(user)
        mask = np.zeros((25,25),np.int8)
        for i in range(25):
            for j in range(25):
                if self.belong_map[(i,j)] in [user, user+3, user+6]: #square
                    mask[(i,j)] = 1
                    for index,i_move in enumerate(square_9[0]):
                        new_i = i + i_move
                        new_j = j + square_9[1][index]
                        if in_map((new_i,new_j)):
                            mask[(new_i,new_j)] = 1
        return mask

    def maskL2__(self, beg):
        return 
        mask = np.zeros((25,25), np.int8)
        if type(beg) == int:
            beg = self.coord_comp(beg)
        for index, move_i in enumerate(square_4[0]):
            new_i = beg[0] + move_i
            new_j = beg[1] + square_4[1][index]
            if in_map((new_i,new_j)):
                mask[new_i][new_j] = 1
        return mask

    def maskL2___(self, move):
        return
        [_, beg, end, _, _] = move
        beg = self.coord_comp(beg)
        end = self.coord_comp(end)
        mask = np.zeros((25,25), np.int8)
        mask[(12+end[0]-beg[0], 12+end[1]-beg[0])] = 1
        return mask
                    

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
                


def in_map(coord: tuple) -> bool:
    return (
        coord[0] >= 0 and 
        coord[1] >= 0 and 
        coord[0] < 25 and 
        coord[1] < 25
    )