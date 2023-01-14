from concurrent.futures import process
import os,sys,json
from random import shuffle
import multiprocessing as mp
from functools import  partial

def r_d(path):

    file = open(path,"r",encoding='utf-8')
    data = json.load(file)
    file.close()
    return data


if __name__ == '__main__':
    base_path = "E:\\CodePalace\\cpp code\\AI-game\\Generals.io_crawl\\dataset\\json\\"
    path_child = [base_path + i for i in os.listdir(base_path)]
    path_leaf = []
    for i in path_child:
        if "zip" in i: continue
        path_leaf += [i + "\\" + j for j in os.listdir(i)]
    shuffle(path_leaf)

    data_all = []
    print("len: ", len(path_leaf))
    print("begin merge")
    pool  = mp.Pool(mp.cpu_count())
    result = list(pool.map(r_d, path_leaf))
    pool.close()
    pool.join()
    print("merge done")
    print("begin to store as .json file")
    with open("./data_all.json","a+") as f:
        json.dump(result,f)
    print("store done")