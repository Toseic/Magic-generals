from feature import G_game 

steps = [(-1,0), (1,0), (0,-1), (0,1)]

def get_max_armies(game: G_game, user: int):
    index ,max_armies = (0,0), 0
    for i in range(game.height):
        for j in range(game.width):
            if game.belong_map[i][j] in [user, user+3, user+6] and max(game.armies_user_map[user][i][j], game.users_map[user][i][j]) > max_armies:
                index, max_armies = (i,j), max(game.armies_user_map[user][i][j], game.users_map[user][i][j])
    return index, max_armies

class Priority():
    # 优先级类
    # place:
    #     1, 2, 3: 对方士兵，城市，基地
    #     0: free
    #     -1, -2, -3:我方士兵，城市，基地
    #     -4：mountain
    def __init__(self, user, place, armies):
        if place in [user, user+3, user+6]:
            self.place = - (place - user) / 3 - 1
        elif place in [1-user, 1-user+3,1-user+6]:
            self.place = (place + user - 1) / 3 + 1
        elif place == 5 or place == -2:
            self.place = 0
        else:
            self.place = -4
        self.armies = armies
        
    def _lt_(self, other):
        if self.place == other.place:
            return self.armies < other.armies
        return self.place < other.place

def build_value(game: G_game, user: int): # 高阶函数，返回在game, user条件下的value函数
    def value(coord):
        return Priority(user, game.belong_map[coord], max(game.armies_user_map[0][coord], game.armies_user_map[1][coord], game.users_map[0][coord], game.users_map[1][coord]))
    return value

def not_naive(game: G_game, user: int, turn: int):
    start = get_max_armies(game, user)[0]
    legal_steps = []
    for step in steps:
        goal = (start[0] + step[0], start[1] + step[1])
        if goal[0] in range(game.height) and goal[1] in range(game.width): # 合法的行进
            legal_steps.append(goal)
    legal_steps.sort(key=build_value(game, user), reverse=True) # 反向排序，第一个即为优先级最高
    end = legal_steps[0]
    return [user, start[0]*game.width + start[1], end[0]*game.width + end[1], False, turn]
