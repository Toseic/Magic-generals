import torch
import numpy as np

# 0 user's square+cities
# 1 enemy's square+cities
# 2 user's city
# 3 enemy's city
# 4 user's general
# 5 enemy's general
# 6 free cities
# 7 mountain
# 8 add info1: turn%2
# 9 add info2: 50 - turn%50

def Adapter(v_f_l, id, turn):
    info = np.zeros((10,25,25))
    info[7] = np.ones((1,25,25))*-1

    height = len(v_f_l)
    width = len(v_f_l[0])
    for i in range(height):
        for j in range(width):
            data = v_f_l[i][j]
            if not data[0]: continue
            if data[1] != 3:
                info[7][i][j] = 0
            # city
            if data[1] == 1:
                army_num = data[2][0][0]
                if data[2][0][1] == -1:
                    info[6][i][j] = army_num
                elif data[2][0][1] == id:
                    info[2][i][j] = army_num
                    info[0][i][j] = army_num
                elif data[2][0][1] == 1-id:
                    info[3][i][j] = army_num                 
                    info[1][i][j] = army_num        

            # square
            elif data[1] == 0:
                if not data[2]: continue
                army_num = data[2][0][0]
                data_id = data[2][0][1]
                if data_id == id:
                    info[0][i][j] = army_num
                elif data_id == 1-id:
                    info[1][i][j] = army_num 
            # general         
            elif data[1] == 2:
                army_num = data[2][0][0]
                data_id = data[2][0][1]
                if data_id == id:
                    info[4][i][j] = 1
                    info[2][i][j] = army_num 
                    info[0][i][j] = army_num
                elif data_id == 1-id:
                    info[5][i][j] = 1
                    info[3][i][j] = army_num
                    info[1][i][j] = army_num 

    info[8] = np.int8(info[2] > np.zeros((25,25))) * (turn%2)
    info[9] = np.int8(info[0] > np.zeros((25,25))) * (turn%2)
    return info, info[0].copy()