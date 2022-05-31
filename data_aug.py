import numpy as np
import random


def aug(data, rot_time, flip_dim):
    data = np.rot90(data,rot_time,(-2,-1))
    data = np.flip(data,[flip_dim,])
    return data


def data_aug(data: list):
    # 数据增强
    rot_time = random.randint(0,4)
    flip_dim = random.choice([-1,-2])
    dataold = data[0][:]
    datanew = []
    for i in dataold:
        datanew.append(aug(i,rot_time,flip_dim)) 
    data.append(datanew)
    return data
