import os,sys,json,enum,time
import numpy as np

sys.path.append("./general/")

class Place(enum.Enum):
    mountain = -1
    null = -2
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

        for mountain in self.mountains:
            self.geogra_map[(self.coord_comp(mountain))] = -1
        for index,army in enumerate(self.cities):
            coord = self.coord_comp(army)
            self.armies_free_map[coord] = self.cityArmies[index]*-1

    def place_check(self,coord):
        if type(coord) == int: 
            coord = self.coord_comp(coord)
        if self.geogra_map[coord] == -1:
            return Place.mountain
        if self.armies_user_map[0][coord] != 0:
            return Place.city_1
        if self.armies_user_map[1][coord] != 0:
            return Place.city_2
        if self.armies_free_map[coord] != 0:
            return Place.city_free
        if self.generals_map[0][coord] == 1:
            return Place.general_1
        if self.generals_map[1][coord] == 1:
            return Place.general_2
        if self.users_map[0][coord] > 0:
            return Place.occupy_1
        if self.users_map[1][coord] > 0:
            return Place.occupy_2
        return Place.null

    def add_per_turn(self):
        for i in range(self.height):
            for j in range(self.width):
                for z in [0,1]:
                    if self.armies_user_map[(z,i,j)] > 0:
                        if self.armies_user_map[(z,i,j)] == 0.5:
                            self.armies_user_map[(z,i,j)] = 0
                        self.armies_user_map[(z,i,j)] += 1

    def add_per_25turn(self):
        for i in range(self.height):
            for j in range(self.width):
                for z in [0,1]:
                    if self.users_map[(z,i,j)] > 0:
                        self.users_map[(z,i,j)] += 1
                    if self.armies_user_map[(z,i,j)] > 0:
                        if self.armies_user_map[(z,i,j)] == 0.5:
                            self.armies_user_map[(z,i,j)] = 0
                        self.armies_user_map[(z,i,j)] += 1

    def move(self, info:list):
        [user, beg, end, half, turn] = info
        enemy = 1- user
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
        if half:
            movenum = int(beg_place_num / 2)
        else: movenum = beg_place_num - 1
        if beg_type.value == user:
            self.users_map[user][beg] -= movenum
        else:
            self.armies_user_map[user][beg] -= movenum
        
        if (end_type.value in [Place.null.value, user]):
            self.users_map[user][end] += movenum

        elif end_type.value == 1-user:
            enemy_num = int(self.users_map[1-user][end])
            num_gap = enemy_num - movenum
            if num_gap > 0:
                self.users_map[1-user][end] = num_gap
            elif num_gap < 0:
                self.users_map[1-user][end] = 0
                self.users_map[user][end] = num_gap*-1
            else:
                self.users_map[user][end] = 0
                self.users_map[1-user][end] = 0

        elif end_type == Place.city_free:
            city_num = int(self.armies_free_map[end])
            num_gap = city_num + movenum
            if num_gap < 0:
                self.armies_free_map[end] = num_gap
            elif num_gap > 0:
                self.armies_free_map[end] = 0
                self.armies_user_map[user][end] = num_gap
            else:
                self.armies_free_map[end] = 0.5

        elif end_type.value in [6+user,3+user]: # user's city 
            self.armies_user_map[user][end] += movenum

        elif end_type.value == 7-user: # enemy's city
            city_num = int(self.armies_user_map[1-user][end])
            num_gap = city_num - movenum
            if num_gap > 0:
                self.armies_user_map[1-user][end] = num_gap
            elif num_gap < 0:
                self.armies_user_map[user][end] = num_gap*-1
                self.armies_user_map[1-user][end] = 0
            else:
                self.armies_user_map[1-user][end] = 0.5

        elif end_type.value == 4-user: # enemy's general
            city_num = int(self.armies_user_map[1-user][end])
            num_gap = city_num - movenum
            if num_gap > 0:
                self.armies_user_map[1-user][end] = num_gap
            elif num_gap < 0:
                self.armies_user_map[user][end] = num_gap*-1
                self.armies_user_map[1-user][end] = 0
                self.gameover = [True,user]
            else:
                self.armies_user_map[1-user][end] = 0.5
        



def rwc(show_str,color_code,status_code = 0):
    '''
    color: ['black','red','green','yellow','blue','magenta','cyan_blue','white']
    '''
    #前景色: 30（黑色）、31（红色）、32（绿色）、 33（黄色）
    # 34（蓝色）、35（洋 红）、36（青色）、37（白色）
    show_str = str(show_str)
    # print(type(color_code))
    if type(color_code) == type(Color.blue):
        color_code = color_code.value
    return "\033[{};{}m".format(status_code,color_code)+show_str+"\033[0;0m"  

def show(game: G_game):
    
    for i in range(game.height):
        for j in range(game.width):
            num1,num2 = int(game.users_map[0][(i,j)]),int(game.users_map[1][(i,j)])
            assert num1 == 0 or num2 == 0 ,"ERROR: num1={},num2={}".format(num1,num2)
            num1_str,num2_str = '{:<4d}'.format(num1), '{:<4d}'.format(num2)

            if game.geogra_map[(i,j)] == -1:
                print(rwc("M",Color.green),end='   ')
            elif game.armies_free_map[(i,j)] < 0:
                num = int(game.armies_free_map[(i,j)]*-1)
                num_str = '{}'.format(num)
                print(rwc(num_str,Color.yellow),end=" "*(4-len(num_str)))
            elif game.generals_map[0][(i,j)]:
                num = int(game.armies_user_map[0][(i,j)])
                print(rwc(num,Color.blue,1),end=" "*(4-len(str(num))))
            elif game.generals_map[1][(i,j)]:
                num = int(game.armies_user_map[1][(i,j)])
                print(rwc(num,Color.red,1),end=" "*(4-len(str(num))))    
            elif game.armies_user_map[0][(i,j)] > 0:
                num = int(game.armies_user_map[0][(i,j)])
                num_str = '{}'.format(num)
                print(rwc(num_str,Color.blue,7),end=" "*(4-len(num_str)))
            elif game.armies_user_map[1][(i,j)] > 0:
                num = int(game.armies_user_map[1][(i,j)])
                num_str = '{}'.format(num)
                print(rwc(num_str,Color.red,7),end=" "*(4-len(num_str)))
    
            else:
                if num1 > 0:
                    print(rwc(num1_str, Color.blue),end='')
                elif num2 > 0:
                    print(rwc(num2_str, Color.red),end='')
                else:
                    print("0   ",end='')

        print()


if __name__ == '__main__':

    file = open("E:\\CodePalace\\cpp code\\AI-game\\Generals.io_crawl\\dataset\\json\\json1\\ruwQa4Wmq.json","r")
    data = json.load(file)
    game = G_game(
        [data['mapWidth'], data['mapHeight']],
        data['cities'],
        data['cityArmies'],
        data['generals'],
        data['mountains'],
    )
    game.init_work()
    turn = -1
    point = 0
    while True:
        i=os.system("cls")
        turn += 1
        if turn != 0 :
            if turn % 2 == 0:
                game.add_per_turn()
            if turn % 50 == 0:
                game.add_per_25turn()
        print("turn: ", turn)
        show(game)
        if (point == len(data["moves"])):
            break
        move_info = data["moves"][point]
        while (move_info[-1] == turn):
            game.move(move_info)
            point+= 1
            if (point == len(data["moves"])):
                break
            move_info = data["moves"][point]
        a = input("pause:")
    # time.sleep(0.2)
# show(game)
