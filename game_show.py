from feature import *

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

            assert num1 == 0 or num2 == 0 ,\
                "ERROR: num1={},num2={},place:({},{})".format(num1,num2,i,j)

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
    turn = 0
    point = 0
    while True:
        if game.gameover[0]:
            break
        else:
            print('\033c',end='')
        if turn != 0 :
            if turn % 2 == 0:
                game.add_per_turn()
            if turn % 50 == 0:
                game.add_per_25turn()
        num = game.sum_army()
        print("turn: ", turn, "  num: [{}|{}] [{}|{}] ".
            format(int(num[0]),int(num[1]),int(num[2]),int(num[3])))
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
        # if turn >= 140:
        # a = input("pause:")
        time.sleep(0.8)
        turn += 1
    num = game.sum_army()

# show(game)