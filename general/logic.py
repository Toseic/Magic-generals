#尚未解决王城战争相等问题！！！

import pygame, collections, random, threading
from naive import naive


class G_game:
    def __init__(self):
        self.map_list = [[[0, []]for i in range(50)] for j in range(50)]
        self.city_list=[]
        self.water_list=[]
        self.cap_list=[[] for i in range(8)]
        self.army_list=[]


    def map_initialize(self):
        for i in range(1,49):
            for j in range(1,49):
                if random.random() > 0.985-0.005*max(abs(i-14.5),abs(j-14.5)):
                    self.map_list[i][j][0] = 3

        for i in range(1,49):
            for j in range(1,49):
                if not self.map_list[i][j][0]:
                    k=sum([self.map_list[i+m][j+n][0]==3 for m in range(-1,2) 
                        for n in range(-1,2)])
                    if random.random() < 0.05*k:
                        self.map_list[i][j][0] = -1

        for i in range(1,49):
            for j in range(1,49):
                if self.map_list[i][j][0] == -1:
                    self.map_list[i][j][0] = 3
        #water initialize
        for i in range(50):
            for j in [0,49]:
                self.map_list[i][j][0] = self.map_list[j][i][0] = 4

        for i in range(1,49):
            for j in range(1,49):
                if not self.map_list[i][j][0]:
                    k=sum([self.map_list[i+m][j+n][0]==3 for m in range(-1,2) for n in range(-1,2)])
                    if random.random() < 0.05+0.01*k:
                        self.map_list[i][j][0] = 4
                        self.water_list.append(self.map_list[i][j])


        for i in range(1,11):
            for j in range(i+2,24-i):
                if not self.map_list[i][j][0]:
                    self.cap_list[0].append([i,j])
                if not self.map_list[j][i][0]:
                    self.cap_list[1].append([j,i])
                if not self.map_list[49-i][j][0]:
                    self.cap_list[2].append([49-i,j])
                if not self.map_list[j][49-i][0]:
                    self.cap_list[3].append([j,49-i])
                if not self.map_list[i][49-j][0]:
                    self.cap_list[4].append([i,49-j])
                if not self.map_list[49-j][i][0]:
                    self.cap_list[5].append([49-j,i])
                if not self.map_list[49-i][49-j][0]:
                    self.cap_list[6].append([49-i,49-j])
                if not self.map_list[49-j][49-i][0]:
                    self.cap_list[7].append([49-j,49-i])
        for i in range(8):
            my_cap=random.sample(self.cap_list[i],1)[0]
            self.map_list[my_cap[0]][my_cap[1]][0]=2
            self.map_list[my_cap[0]][my_cap[1]][1].append([1, i])
            self.cap_list[i]=my_cap
            self.city_list.append(self.map_list[my_cap[0]][my_cap[1]])
        random.shuffle(self.cap_list)
        #city initialize
        for i in range(1,49):
            for j in range(1,49):
                if not self.map_list[i][j][0] and random.random()>0.98:
                    self.map_list[i][j][0]=1
                    self.map_list[i][j][1].append([int(abs(random.gauss(30,3))),-1])
                    self.city_list.append(self.map_list[i][j])
    
    def cap_change(self, a, b):
        global game_running
        self.army_list[a].defeat(b)
        if len(self.army_list) == 1:
            game_running = 0


    def battle(self, battlefield):
        if len(battlefield[1])>1:
            for i in battlefield[1][0:-2]:
                if i[1]==battlefield[1][-1][1]:
                    battlefield[1][-1][0]+=i[0]
                    battlefield[1].remove(i)
                    if len(battlefield[1]) == 1:
                        return
                    break
            if battlefield[0]==2:
                cap_defender=battlefield[1][0][1]
            battlefield[1].sort()
            battlefield[1][0][0]-=battlefield[1][1][0]
            if battlefield[1][0][0]:
                battlefield[1] = [battlefield[1][0]]
            else:
                battlefield[1] = []
            if len(battlefield[1]) and battlefield[1][0][1]!=cap_defender:
                self.cap_change(cap_defender,battlefield[1][0][1])
 

    def city_expansion(self):
        for i in self.city_list:
            self.map_list[i[0]][i[1]][1][0]+=1
    
    def city_compute(self):
        for i in self.city_list:
            if i[1][0][1]!=-1:
                i[1][0][0]+=1
        for i in self.water_list:
            if len(i[1])!=0:
                i[1][0][0]-=1

    def in_de_compute(self):
        for i in self.map_list:
            for block in i:
                if len(block[1]):
                    if not block[0]:
                        block[1][0]+=1
                    elif block[0]==1 and block[1][0][1] == -1:
                        block[1][0][1]+=5

    def battle_compute(self):
        for i in range(8):
            legal_act_completed = 0
            while not legal_act_completed and len(act_list[i]):
                acting = act_list[i].popleft()
                army_moving = self.map_list[acting[0]][acting[1]][1]
                if acting[3] == 0:
                    acting[0]-=1
                elif acting[3] == 1:
                    acting[0]+=1
                elif acting[3] == 2:
                    acting[1]-=1
                else:
                    acting[1]+=1
                if len(army_moving) and army_moving[-1][0]>1 and army_moving[-1][1] == i and \
                    0<=acting[-1]<50 and 0<=acting[-1]<50 and self.map_list[acting[0]][acting[1]][0] != 3:
                    self.map_list[acting[0]][acting[1]][1].append([acting[2],army_moving[-1][1]])
                    army_moving[-1][0]-=acting[2]
                    legal_act_completed = 1
        del acting, army_moving
        for i in self.map_list:
            for block in i:
                self.battle(block)

    def visual_field(self, k):
        visual_list=[[0 for i in range(52)]for j in range(52)]
        for i in range(50):
            for j in range(50):
                if len(self.map_list[i][j][1]) and self.map_list[i][j][1][0][1] == k:
                    visual_list[i+1][j+1]=1
        for i in range(52):
            for j in range(52):
                if visual_list[i][j]==1:
                    visual_list[i-1][j-1]=visual_list[i-1][j]=visual_list[i-1][j+1]=visual_list[i][j-1]=visual_list[i][j+1]=visual_list[i+1][j-1]=visual_list[i+1][j]=visual_list[i+1][j+1]=2
        for i in range(52):
            for j in range(52):
                if visual_list[i][j]==2:
                    visual_list[i][j]=1
        visual_field_list=[[[False,-1,[]]for i in range(50)]for j in range(50)]
        for i in range(50):
            for j in range(50):
                if visual_list[i+1][j+1]:
                    visual_field_list[i][j][0] = True
                    visual_field_list[i][j][1] = self.map_list[i][j][0]
                    if len(self.map_list[i][j][1]):
                        visual_field_list[i][j][2].append(
                            [
                                self.map_list[i][j][1][0][0],
                                self.map_list[i][j][1][0][1]
                            ]
                        )
                elif self.map_list[i][j][0] == 3 or self.map_list[i][j][0] == 4:
                    visual_field_list[i][j][1] = self.map_list[i][j][0]
        return visual_field_list

    def ai_act(self, k):
        for i in range(k,8):
            act_list[i].append(naive(i,self.visual_field(i)))
        return


class army:
    def __init__(self, id, my_cap):
        self.id = id
        self.my_cap = my_cap

    def defeat(self, win_id, game: G_game):
        for i in range(1,49):
            for j in range(1,49):
                if game.map_list[i][j][1][1] == self.id:
                    game.map_list[i][j][1][0] = game.map_list[i][j][0]//2+1
                    game.map_list[i][j][1][1]=win_id
        game.map_list[self.my_cap[0]][self.my_cap[1]][0]=1



def man_dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

def expansion(field):
    if not field and field[1] != []:
        field[1][0][0]+=1

def game_listen():
    while 1:
        event_list.append(pygame.event.get())
    return

def game_ui(game: G_game):
    tiktok=pygame.time.Clock()
    ui_compute_clock = 15
    in_de_compute_clock = 50
    while game_running:
        tiktok.tick(30)
        game_event_to_act()
        ui_compute_clock-=1
        if not ui_compute_clock:
            ui_compute_clock=15
            game.game_compute()
            game.ai_act(1)
        game_display()
    return



def ai_game(game: G_game):
    game.map_initialize()
    for i in range(8):
        game.army_list.append(army(i,game.cap_list[i]))
    game_running=1
    in_de_compute_clock=50
    while game_running:
        map_print()
        game.ai_act(0)
        game.game_compute()

def game_event_to_act():
    return


def game_display():
    return





        

def game_main():
    game = G_game
    game.map_initialize()
    # army_list=[]
    event_list=[]
    for i in range(8):
        game.army_list.append(army(i))
    game_running=1
    thread_event=threading.Thread(target=game_listen, args=())
    thread_logic=threading.Thread(target=game_ui, args=(game,))
    while game_running:
        thread_event.start()
        thread_logic.start()
    return

def main():
    pygame.init()
    game_main()
    pygame.quit()
    return


def map_print(game: G_game):
    # row_list=[]
    for i in range(50):
        x=['x' if game.map_list[i][j][0]==3 else 'o' 
            if game.map_list[i][j][0]==4 else ' ' 
            if not len(game.map_list[i][j][1]) else 'c' 
            if  game.map_list[i][j][1][0][1]==-1 else game.map_list[i][j][1][0][1] for j in range(50)]
        print(*x,sep=' ')


if __name__ =="__main__":
    # 入口
    event_list=collections.deque([])
    act_list=[collections.deque([]) for i in range(8)]
    main()
# map_initialize()
# print('\n')
# text=open('D:\\Desktop\\桌面\\others\\XieYinLun\\codes\\general\\text.txt','w')
# for i in range(50):
#     x=[' ' if map_list[i][j][0]==0 else'x' if map_list[i][j][0]==3 else 'o' if map_list[i][j][0]==4 else '*' if  map_list[i][j][0]==2 else map_list[i][j][1][0][0] for j in range(50)]
#     for j in x:
#         text.write(str(j))
#         text.write('\t')
#     text.write('\n')
# text.close()