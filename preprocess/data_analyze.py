import os
from random import shuffle
import multiprocess as mp
import json

def r_d(path):
    with open(path,"r",encoding='utf-8') as file:
        data = json.load(file)
        file.close()
        check_one = 0
        for i in data['moves']:
            if i[3] == 1:
                check_one += 1
        return [len(data['moves']), check_one]

if __name__ == '__main__':

    base_path = "E:\\CodePalace\\cpp code\\AI-game\\Generals.io_crawl\\dataset\\json\\"
    path_child = [base_path + i for i in os.listdir(base_path)]
    path_leaf = []
    for i in path_child:
        if "zip" in i: continue
        path_leaf += [i + "\\" + j for j in os.listdir(i)]
    shuffle(path_leaf)

    data_all = []
    # print(r_d(path_leaf[0]))
    print("len: ", len(path_leaf))
    print("script begin")
    pool  = mp.Pool(mp.cpu_count())
    result = list(pool.map(r_d, path_leaf))
    pool.close()
    pool.join()
    print("begin comp")
    num = [0,0]
    for i in result:
        num[0] += i[0]
        num[1] += i[1]
    print(num)
