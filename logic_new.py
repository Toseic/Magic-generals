#解决了。


import pygame, collections, random, threading
from naive import naive
import sys


class general_game:
    def __init__(self):
        self.width = random.randint(18, 23)
        self.length = random.randint(18, 23)
        self.size = self.width*self.length
        self.draw_start_point = [400-self.width*12.5,300-self.length*12.5]
        self.map_list = [[[0, []]for i in range(self.width)]for j in range(self.length)]
        self.visual_field_list=[[[[False,-1,[]]for i in range(self.width)]for j in range(self.length)] for k in [0, 1]]
        self.city_list=[]
        # self.water_list=[]
        self.general_list=[]
        self.army_list=[]
        self.general_battle_list=[]
        self.in_de_compute_clock=50

    def map_initialize(self):
        #mountain initialize
        for i in range(1,self.length-1):
            for j in range(1,self.width-1):
                if random.random() > 0.8:
                    self.map_list[i][j][0] = 3
        for i in range(1,self.length-1):
            for j in range(1,self.width-1):
                if not self.map_list[i][j][0]:
                    k=sum([self.map_list[i+m][j+n][0]==3 for m in [-1,1] 
                        for n in [-1,1]])-sum([self.map_list[i+m][j+n][0]==3 for m in range(-1,2) 
                        for n in [[1,-1],[0]][m]])
                    if random.random() < 0.1*k:
                        self.map_list[i][j][0] = -1
        for i in range(1,self.length-1):
            for j in range(1,self.width-1):
                if self.map_list[i][j][0] == -1:
                    self.map_list[i][j][0] = 3
        #water initialize
        # for i in range(self.width):
        #     self.map_list[0][i][0] = self.map_list[-1][i][0] = 4
        #     self.water_list.extend(self.map_list[0][i],self.map_list[-1][i])
        # for i in range(1,self.length-1):
        #     self.map_list[i][0][0] = self.map_list[i][-1][0] = 4
        #     self.water_list.extend(self.map_list[i][0],self.map_list[i][-1])
        # for i in range(1,self.length-1):
        #     for j in range(1,self.width-1):
        #         if not self.map_list[i][j][0]:
        #             k=sum([self.map_list[i+m][j+n]==3 for m in range(-1,2) for n in range(-1,2)])
        #             if random.random() < 0.02+0.01*k:
        #                 self.map_list[i][j][0] = 4
        #                 self.water_list.append(self.map_list[i][j])
        #general initialize
        for i in range(1,self.length-1):
            for j in range(1, self.width-1):
                if not self.map_list[i][j][0]:
                    self.general_list.append([i,j])
        while True:
            ge_ge=random.sample(self.general_list,2) #general_generation
            if man_dist(ge_ge[0][0],ge_ge[0][1],ge_ge[1][0],ge_ge[1][1]) >= min(self.width,self.length):
                break
        self.general_list=[self.map_list[ge_ge[0][0]][ge_ge[0][1]], self.map_list[ge_ge[1][0]][ge_ge[1][1]]]
        for i in [0, 1]:
            self.general_list[i][0] = 2
            self.general_list[i][1].append([1, i])
        self.city_list.extend(self.general_list)
        #city initialize
        city_number=int(self.size/40)
        city_number=random.randint(city_number-2,city_number+2)
        while city_number:
            i=random.randint(1,self.length-1)
            j=random.randint(1,self.width-1)
            if not self.map_list[i][j][0]:
                city_number-=1
                self.map_list[i][j][0]=1
                self.map_list[i][j][1].append([int(random.randint(40,50)),-1])
                self.city_list.append(self.map_list[i][j])
        return
    
    def general_change(self, a, *args):
        global game_running, winner
        if args:
            game_running = 0
            winner = -1
            for i in self.map_list:
                for block in i:
                    if block[1] and block[1][0][1] != -1:
                        block[1].clear()
            return
        else:
            b=abs(a-1)
            self.army_list[a].defeat(b, self)
            winner = b
            game_running = 0
            return


    def battle(self, battlefield):
        if len(battlefield[1])>1:
            for i in range(1,len(battlefield[1])):
                if battlefield[1][i][1]==battlefield[1][0][1]:
                    battlefield[1][0][0]+=battlefield[1].pop(i)[0]
                    if len(battlefield[1]) == 1:
                        return
                    break
            if battlefield[0]==2:
                self.general_battle_list.append(battlefield)
                return
            else:
                battlefield[1].sort(reverse=True)
                battlefield[1][0][0]-=battlefield[1].pop(1)[0]
                if not battlefield[1][0][0]:
                    battlefield[1].clear()
                return
        return
 

    def general_battle(self):
        global game_running
        loser=[]
        for i in self.general_battle_list:
            i[1][0][0]-=i[1].pop(1)[0]
            if i[1][0][0]<0:
                loser.append(i[1][0][1])
        if not len(loser):
            self.general_battle_list.clear()
        else:
            self.general_change(*loser)
        return

    
    def city_compute(self):
        for i in self.city_list:
            if i[1][0][1]!=-1:
                i[1][0][0]+=1
        # for i in self.water_list:
        #     if len(i[1])!=0:
        #         i[1][0][0]-=1


    def in_de_compute(self):
        for i in self.map_list:
            for block in i:
                if block[1]:
                    if not block[0]:
                        block[1][0][0]+=1
                    elif block[0]==1 and block[1][0][1] == -1:
                        block[1][0][0]+=0


    def battle_compute(self):
        for i in [0,1]:
            legal_act_completed = 0
            while not legal_act_completed and len(act_list[i]):
                acting = act_list[i].popleft()
                if 0<=acting[0]<self.length and 0<=acting[1]<self.width and 0<=acting[3]<self.length and 0<=acting[4]<self.width:
                    block_moving = self.map_list[acting[0]][acting[1]][1]
                    if block_moving and block_moving[0][0]>1 and block_moving[0][1] == i and self.map_list[acting[3]][acting[4]][0] != 3:
                        if not acting[2]:
                            army_moving = block_moving[0][0]-1
                        else:
                            army_moving = block_moving[0][0]//2
                        self.map_list[acting[3]][acting[4]][1].append([army_moving,block_moving[0][1]])
                        block_moving[0][0]-=army_moving
                        legal_act_completed = 1
                    del block_moving
                del acting
        for i in self.map_list:
            for block in i:
                self.battle(block)
        if self.general_battle_list:
            self.general_battle()
        return

    def game_compute(self):
        self.in_de_compute_clock-=1
        self.battle_compute()
        if not self.in_de_compute_clock%2:
            self.city_compute() #also water
        if not self.in_de_compute_clock:
            self.in_de_compute()
            self.in_de_compute_clock=50
        return

    def visual_field_list_generate(self):
        self.visual_field_list=[[[[False,-1,[]]for i in range(self.width)]for j in range(self.length)] for k in [0, 1]]
        for k in [0, 1]:
            visible_check=[[0 for i in range(self.width+2)]for j in range(self.length+2)]
            for i in range(self.length):
                for j in range(self.width):
                    if self.map_list[i][j][1] and self.map_list[i][j][1][0][1] == k:
                        visible_check[i+1][j+1]=1
            for i in range(1,self.length+1):
                for j in range(1,self.width+1):
                    if not visible_check[i][j] and 1 in [visible_check[i-1][j-1],visible_check[i-1][j],visible_check[i-1][j+1],visible_check[i][j-1],visible_check[i][j+1],visible_check[i+1][j-1],visible_check[i+1][j],visible_check[i+1][j+1]]:
                        visible_check[i][j]=2
            for i in range(self.length+2):
                for j in range(self.width+2):
                    if visible_check[i][j]==2:
                        visible_check[i][j]=1

            for i in range(self.length):
                for j in range(self.width):
                    if visible_check[i+1][j+1]:
                        self.visual_field_list[k][i][j][0] = True
                        self.visual_field_list[k][i][j][1] = self.map_list[i][j][0]
                        if self.map_list[i][j][1]:
                            self.visual_field_list[k][i][j][2].append(
                                [
                                    self.map_list[i][j][1][0][0],
                                    self.map_list[i][j][1][0][1]
                                ]
                            )
                    elif self.map_list[i][j][0] == 3:
                        self.visual_field_list[k][i][j][1] = 3
        return

    def ai_act(self, k):
        for i in range(k,2):
            act_list[i].append(naive(i,self.length,self.width,self.visual_field_list[i]))
        return


class army:
    def __init__(self, id, general, color):
        self.id = id
        self.general = general
        self.color = color

    def defeat(self, win_id, game: general_game):
        for i in range(1,game.length-1):
            for j in range(1,game.width-1):
                if game.map_list[i][j][1] and game.map_list[i][j][1][0][1] == self.id:
                    game.map_list[i][j][1][0] = game.map_list[i][j][0]//2+1
                    game.map_list[i][j][1][0][1]=win_id
        game.map_list[self.general[0]][self.general[1]][0]=1



def man_dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

class event_listen:
    def __init__(self, game:general_game):
        self.width = [game.draw_start_point[0], game.draw_start_point[0]+25*game.width]
        self.length = [game.draw_start_point[1], game.draw_start_point[1]+25*game.length]
        self.down_pos = []
        self.up_pos = []
        self.choose_block = []
        self.action = []
    
    def listen(self, mode):
        global running, act_list
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0
                return
            if not mode:
                # if event == pygame.MOUSEMOTION:
                #     if self.width[0]<=event.pos[0]<=self.width[1] and len[0]<=event.pos[1]<len[1]:
                #         new_motion=[int((event.pos[0]-self.width[0])/25)+1,int((event.pos[1]-self.length[0])/25)+1]
                #     else:
                #         new_motion=[]
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.down_pos=[int((event.pos[0]-self.width[0])/25),int((event.pos[1]-self.length[0])/25)]
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.up_pos=[int((event.pos[0]-self.width[0])/25),int((event.pos[1]-self.length[0])/25)]
                    if self.down_pos==self.up_pos:
                        if self.up_pos:
                            if not self.choose_block or self.choose_block[:2]!=self.up_pos:
                                self.choose_block=[self.up_pos[1], self.up_pos[0], 0]
                            else:
                                self.choose_block[2] = not self.choose_block[2]
                    else:
                        self.choose_block.clear()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, 119]:
                        self.choose_block.append(self.choose_block[0]-1)
                        self.choose_block.append(self.choose_block[1])
                        self.choose_block.append(0)
                    elif event.key in [pygame.K_LEFT, 97]:
                        self.choose_block.append(self.choose_block[0])
                        self.choose_block.append(self.choose_block[1]-1)
                        self.choose_block.append(1)
                    elif event.key in [pygame.K_DOWN, 115]:
                        self.choose_block.append(self.choose_block[0]+1)
                        self.choose_block.append(self.choose_block[1])
                        self.choose_block.append(2)
                    elif event.key in [pygame.K_RIGHT, 100]:
                        self.choose_block.append(self.choose_block[0])
                        self.choose_block.append(self.choose_block[1]+1)
                        self.choose_block.append(3)
                    if len(self.choose_block)>4:
                        act_list[0].append([self.choose_block[i] for i in range(6)])
                        print(act_list[0])
                        self.choose_block=self.choose_block[-3:-1]
                        self.choose_block.append(0)
        return

# def game_listen(game:general_game):
#     global game_running, running, act_list
#     width = [game.draw_start_point[0], game.draw_start_point[0]+25*game.width]
#     length = [game.draw_start_point[1], game.draw_start_point[1]+25*game.length]
#     choose_block = []
#     action = []
#     print("3")
#     while game_running and running:
#         for event in pygame.event.get():
#             if event == pygame.QUIT:
#                 running = 0
#                 break
#             elif event == pygame.MOUSEMOTION:
#                 if width[0]<=event.pos[0]<=width[1] and len[0]<=event.pos[1]<len[1]:
#                     new_motion=[int((event.pos[0]-width[0])/25)+1,int((event.pos[1]-length[0])/25)+1]
#                 else:
#                     new_motion=[]
#             elif event == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 down_pos=new_motion
#             elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
#                 up_pos=new_motion
#                 if down_pos==up_pos:
#                     if up_pos:
#                         if not choose_block:
#                             choose_block=[new_motion[0], new_motion[1], 0]
#                         else:
#                             choose_block[2] = 1
#                 else:
#                     choose_block.clear()
#             elif event.tpye == pygame.KEYDOWN:
#                 if event.key in [pygame.K_UP, 119]:
#                     choose_block.append(0)
#                     action.extend(choose_block)
#                     action.append(0)
#                 elif event.key in [pygame.K_LEFT, 97]:
#                     choose_block.append(2)
#                 elif event.key in [pygame.K_DOWN, 115]:
#                     choose_block.append(1)
#                 elif event.key in [pygame.K_RIGHT, 100]:
#                     choose_block.append(3)
#     return


def game_ui(mode, game: general_game):
    global game_running, running
    listen = event_listen(game)
    tiktok=pygame.time.Clock()
    ui_compute_clock = 15
    game.in_de_compute_clock = 50
    if mode:
        while game_running and running:
            tiktok.tick(2)
            game.game_compute()
            game.visual_field_list_generate()
            listen.listen(mode)
            game.ai_act(0)
            game_display(mode, game, listen)
    else:
        while game_running and running:
            tiktok.tick(30)
            ui_compute_clock-=1
            listen.listen(mode)
            if not ui_compute_clock:
                ui_compute_clock=15
                game.game_compute()
                game.visual_field_list_generate()
                game.ai_act(1)
            game_display(mode, game, listen)
    return


# def ai_game(game: general_game):
#     game.map_initialize()
#     for i in range(8):
#         game.army_list.append(army(i,game.general_list[i]))
#     game_running=1
#     in_de_compute_clock=50
#     while game_running:
#         map_print()
#         game.ai_act(0)
#         game.game_compute()


def game_event_to_act():
    global running, event_list
    while len(event_list):
        event_now = event_list.popleft()
        if event_now == pygame.QUIT:
            running = 0
            break

    return

def scoreboard(mode, game: general_game):
    army_number=[0, 0]
    land_number=[0, 0]
    for i in game.map_list:
        for block in i:
            if block[1] and block[1][0][1]!=-1:
                id = block[1][0][1]
                army_number[id]+=block[1][0][0]
                land_number[id]+=1
    if mode:
        text_list=["电脑1", "电脑2"]
    else:
        text_list=["人类", "电脑"]
    if army_number[0]>=army_number[1]:
        display_order=[0, 1]
    else:
        display_order=[1, 0]
    pygame.draw.rect(project, [222,222,222], [game.draw_start_point[0]+25*game.width,game.draw_start_point[1],50,25],0)
    pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width,game.draw_start_point[1],50,25],1)
    display_text("玩家", file_text, 15, [31,31,31], (game.draw_start_point[0]+25*game.width+25,game.draw_start_point[1]+12.5))
    for i in [0, 1]:
        pygame.draw.rect(project, game.army_list[display_order[i]].color, [game.draw_start_point[0]+25*game.width,game.draw_start_point[1]+25+25*i,50,25],0)
        pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width,game.draw_start_point[1]+25+25*i,50,25],1)
        display_text(text_list[display_order[i]], file_text, 15, [222,222,222], (game.draw_start_point[0]+25*game.width+25,game.draw_start_point[1]+37.5+25*i))
    pygame.draw.rect(project, [222,222,222], [game.draw_start_point[0]+25*game.width+50,game.draw_start_point[1],30,25],0)
    pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width+50,game.draw_start_point[1],30,25],1)
    display_text("军队", file_text, 15, [31,31,31], (game.draw_start_point[0]+25*game.width+65,game.draw_start_point[1]+12.5))
    for i in [0, 1]:
        pygame.draw.rect(project, [222,222,222], [game.draw_start_point[0]+25*game.width+50,game.draw_start_point[1]+25+25*i,30,25],0)
        pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width+50,game.draw_start_point[1]+25+25*i,30,25],1)
        display_text(str(army_number[display_order[i]]), file_text, 15, [31,31,31], (game.draw_start_point[0]+25*game.width+65,game.draw_start_point[1]+37.5+25*i))
    pygame.draw.rect(project, [222,222,222], [game.draw_start_point[0]+25*game.width+80,game.draw_start_point[1],30,25],0)
    pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width+80,game.draw_start_point[1],30,25],1)
    display_text("地块", file_text, 15, [31,31,31], (game.draw_start_point[0]+25*game.width+95,game.draw_start_point[1]+12.5))
    for i in [0, 1]:
        pygame.draw.rect(project, [222,222,222], [game.draw_start_point[0]+25*game.width+80,game.draw_start_point[1]+25+25*i,30,25],0)
        pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+25*game.width+80,game.draw_start_point[1]+25+25*i,30,25],1)
        display_text(str(land_number[display_order[i]]), file_text, 15, [31,31,31], (game.draw_start_point[0]+25*game.width+95,game.draw_start_point[1]+37.5+25*i))
    return


def game_display(mode, game: general_game, listen: event_listen):
    global image_list, act_list, file_arrow
    for i in range(game.length):
        for j in range(game.width):
            block=block_paintablize(mode, i, j, game)
            if not block[0]:
                block_rect([63,63,63], i, j, game)
                if block[1] == 3:
                    block_image(0, i, j, game)
            else:
                if block[2]:
                    get_block_army = [block[2][0][0],block[2][0][1]]
                    if get_block_army[1]>-1:
                        block_rect(game.army_list[get_block_army[1]].color, i, j, game)
                    else:
                        block_rect([95,95,95], i, j, game)
                    if block[1] == 1:
                        block_image(1, i, j, game)
                    elif block[1] == 2:
                        block_image(2, i, j, game)
                    block_number(get_block_army[0], i, j, game)
                else:
                    if block[1] == 1:
                        block_rect([95,95,95], i, j, game)
                        block_image(1, i, j, game)
                        block_number(0, i, j)
                        continue
                    elif block[1] == 3:
                        block_rect([127, 127, 127], i, j, game)
                        block_image(0, i, j, game)
                    else:
                        block_rect([191, 191, 191], i, j, game)
    if not mode:
        if listen.choose_block:
            pygame.draw.rect(project, [222, 222, 222], [game.draw_start_point[0]+listen.choose_block[1]*25,game.draw_start_point[1]+listen.choose_block[0]*25,25,25],1)
            if listen.choose_block[2]:
                pygame.draw.rect(project, [222, 222, 222, 0.5], [game.draw_start_point[0]+listen.choose_block[1]*25,game.draw_start_point[1]+listen.choose_block[0]*25,25,25],0)
        if act_list[0]:
            for i in act_list[0]:
                if i[5]==0:
                    display_text("↑", file_arrow, 15, [222, 222, 222], (game.draw_start_point[0]+i[1]*25+12.5,game.draw_start_point[1]+i[0]*25))
                elif i[5]==1:
                    display_text("←", file_arrow, 15, [222, 222, 222], (game.draw_start_point[0]+i[1]*25,game.draw_start_point[1]+i[0]*25+12.5))
                elif i[5]==2:
                    display_text("↓", file_arrow, 15, [222, 222, 222], (game.draw_start_point[0]+i[1]*25+12.5,game.draw_start_point[1]+i[0]*25+25))
                elif i[5]==3:
                    display_text("→", file_arrow, 15, [222, 222, 222], (game.draw_start_point[0]+i[1]*25+25,game.draw_start_point[1]+i[0]*25+12.5))
    scoreboard(mode, game)
    pygame.display.update()
    return


def block_paintablize(mode, i ,j, game:general_game):
    if mode:
        return [True, game.map_list[i][j][0], game.map_list[i][j][1]]
    else:
        return game.visual_field_list[0][i][j]


def block_rect(color, i, j, game:general_game):
    global project
    pygame.draw.rect(project, color, [game.draw_start_point[0]+j*25,game.draw_start_point[1]+i*25,25,25],0)
    pygame.draw.rect(project, [31,31,31], [game.draw_start_point[0]+j*25,game.draw_start_point[1]+i*25,25,25],1)
    return


def block_image(subject, i, j, game:general_game):
    global project, image_list
    project.blit(image_list[subject], (game.draw_start_point[0]+j*25,game.draw_start_point[1]+i*25))
    return


def block_number(n, i, j, game:general_game):
    global project
    display_text(str(n), file_text, 15, [222, 222, 222], (game.draw_start_point[0]+j*25+12.5,game.draw_start_point[1]+i*25+12.5))
    return


def display_text(text, font, size, color, dest):
    sentence = pygame.font.Font(font, size)
    content = sentence.render(text, True, color)
    content_rect = content.get_rect()
    content_rect.center = dest
    project.blit(content, content_rect)
    return

class title_button:
    global project

    def __init__(self, text, font, size, color, background, dest):
        self.text = text
        self.font = font
        self.size = size
        self.color = color
        self.background = background
        self.dest = dest

        self.sentence = pygame.font.Font(self.font, self.size)
        self.content = self.sentence.render(self.text, True, self.color)
        self.content_rect = self.content.get_rect()
        self.content_rect.center = self.dest

        project.blit(self.content, self.content_rect)
        pygame.display.update()

    def choose_title(self, Bool):
        if Bool:
            pygame.draw.rect(project, self.color,
                             [self.content_rect[i] - 10 if i in (0, 1) else self.content_rect[i] + 20 for i in
                              range(4)], 5)
        else:
            pygame.draw.rect(project, self.background,
                             [self.content_rect[i] - 10 if i in (0, 1) else self.content_rect[i] + 20 for i in
                              range(4)], 5)
        pygame.display.flip()

        

def game_main(mode):
    global running, game_running, project
    game = general_game()

    game.map_initialize()
    random.shuffle(color_list)
    for i in [0, 1]:
        game.army_list.append(army(i, game.general_list[i], color_list[i]))
    game_running=1
    project.fill([31, 31, 31])
    game_ui(mode,game)
    return

def main():
    global project, running, file_title, file_text, image_list
    pygame.init()
    project = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("双城之战")
    running = 1
    image_list=[pygame.image.load("mountain.png"),pygame.image.load("city.png"),pygame.image.load("general.png")]
    for i in range(3):
        image_list[i] = pygame.transform.scale(image_list[i], (24, 24))
    project.fill([31,31,31])
    Title_0 = title_button('双 城 之 战', file_title, 127, [222,222,222], [31,31,31], (400, 100))
    Title_1 = title_button('开始对局', file_text, 31, [222,222,222], [31,31,31], (400, 225))
    Title_2 = title_button('模拟对局', file_text, 31, [222,222,222], [31,31,31], (400, 300))
    Title_3 = title_button('操作指南', file_text, 31, [222,222,222], [31,31,31], (400, 375))
    Title_4 = title_button('设置选项', file_text, 31, [222,222,222], [31,31,31], (400, 450))
    Title_5 = title_button('退出游戏', file_text, 31, [222,222,222], [31,31,31], (400, 525))
    Title_Ilist = [Title_0, Title_1, Title_2, Title_3, Title_4, Title_5]
    key = key_1 = 0
    new_motion=0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_RIGHT, 115, 100]:
                    key_1 = key + 1
                elif event.key in [pygame.K_UP, pygame.K_LEFT, 119, 97]:
                    key_1 = key - 1
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if key == 1:
                        game_main(0)
                    if key == 2:
                        game_main(1)
                    if key == 3:
                        game_main(0)
                    if key == 4:
                        game_main(1)
                    if key == 5:
                        running = 0
                        break
            elif event.type == pygame.MOUSEMOTION:
                if 340<=event.pos[0]<=460 and 187.5<=event.pos[1]<562.5:
                    new_motion=int((event.pos[1]-112.5)/75)
                    key_1=new_motion
                else:
                    new_motion=0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                down_pos=new_motion
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                up_pos=new_motion
                if down_pos==up_pos and up_pos:
                    if key == 1:
                        game_main(0)
                    if key == 2:
                        game_main(1)
                    if key == 3:
                        game_main(0)
                    if key == 4:
                        game_main(1)
                    if key == 5:
                        running = 0
                        break
            elif event.type == pygame.QUIT:
                running = 0
                break
        if key_1 != key:
            Title_Ilist[key].choose_title(0)
            if key_1 < 1:
                key_1 = 5
            if key_1 > 5:
                key_1 = 1
            key = key_1
            Title_Ilist[key].choose_title(1)
    pygame.quit()
    return


def map_print(game: general_game):
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
    act_list=[collections.deque([]) for i in [0,1]]
    color_list=[[67,99,216],[255,0,0],[245,130,49],[0,128,128]]
    file_title="font_title.ttf"
    file_text="font_text.otf"
    file_arrow="font_arrow.ttf"
    main()

#act_list=[x, y, if half, turn]

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