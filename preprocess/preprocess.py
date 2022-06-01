from random import shuffle,choice
from feature import G_game as g_game
import numpy as np
import json
from game_show import *
from gc import collect
import multiprocessing as mp
from time import time
from data_aug import data_aug

class G_game(g_game):
    def make(self, move_info: list):
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
        [user,beg,end,half,turn] = move_info
        beg = self.coord_comp(beg)
        end = self.coord_comp(end)
        enemy = 1 - user

        data = np.zeros((10,25,25))
        square_mask = np.int8(self.users_map[user] > np.zeros((25,25)))
        cities_mask = np.int8(self.armies_user_map[user] > np.zeros((25,25)))

        data[0] = self.users_map[user].copy()+self.armies_user_map[user].copy()
        data[1] = self.users_map[enemy].copy()+self.armies_user_map[enemy].copy()
        data[2] = self.armies_user_map[user].copy()
        data[3] = self.armies_user_map[enemy].copy()
        data[4] = np.int8(self.generals_map[user].copy())
        data[5] = np.int8(self.generals_map[enemy].copy())
        data[6] = self.armies_free_map.copy()*-1
        data[7] = np.int8(self.geogra_map.copy()*-1)
        data[8] = np.int8(np.multiply(np.ones((25,25))*(turn % 2), cities_mask))
        data[9] = np.int8(np.multiply(np.ones((25,25))*(50-turn%50), square_mask+cities_mask))

        mask = np.int8(self.maskL1(user))

        data = np.multiply(data, mask)


        legal = np.int8(data[0] > np.ones((25,25)))

        label = np.zeros((2,25,25),np.int8)
        label[0][beg] = 1 
        label[1][(12+end[0]-beg[0], 12+end[1]-beg[1])] = 1
        # label = label.reshape(2,25*25)

        # legal check:
        islegal = True
        if legal[beg] == 0: islegal = False
        if self.geogra_map[end] != 0: islegal = False

        if islegal:
            return data, legal, label
        else:
            return False,False,False


def build(path_or_data):
    choice_pool = [True,True,False,False,False,False]
    shuffle(choice_pool)
    file = None
    if type(path_or_data) == str:
        try:
            file = open(path_or_data,"r")
            data = json.load(file)
        except Exception as e: raise e
    else:
        data = path_or_data
    game = G_game(
        [data['mapWidth'], data['mapHeight']],
        data['cities'],
        data['cityArmies'],
        data['generals'],
        data['mountains'], )
    datas = []
    game.init_work()
    turn,point = 0, 0
    while True:
        if game.gameover[0]:
            break
        if turn != 0:
            if turn % 2 == 0: game.add_per_turn()
            if turn % 50 == 0: game.add_per_25turn()  

        ## debug >>>>>>>
        # show(game)
        # a = input(":")
        # print('\033c',end='')
        ## debug >>>>>>>

        # num = game.sum_army()
        if (point == len(data["moves"])): break
        move_info = data["moves"][point]
        while (move_info[-1] == turn):
            if move_info[3] == 0 and choice(choice_pool):
                data_,legal_,label_ = game.make(move_info)
                
                if type(data_) != bool:
                    rdata = data_aug([[data_,legal_,label_]])
                    datas += rdata

            game.move(move_info)
            point+= 1
            if (point == len(data["moves"])): break
            move_info = data["moves"][point]
        turn += 1
    if type(path_or_data) == str: file.close()
    return datas



def save(results, pack):
    l_r = len(results)
    shuffle(results)
    labels_train = np.array([data[2] for data in results[:int(l_r*4/5)]])
    labels_test = np.array([data[2] for data in results[int(l_r*4/5):]])
    shape1, shape2 = list(labels_train.shape), list(labels_test.shape)
    
    labels_train = labels_train.reshape(shape1[:-2]+[25*25,])
    labels_train = np.argmax(labels_train, axis = -1)
    labels_train = labels_train.reshape(shape1[:-2]+[1,])

    labels_test = labels_test.reshape(shape2[:-2]+[25*25,])
    labels_test = np.argmax(labels_test, axis = -1)
    labels_test = labels_test.reshape(shape2[:-2]+[1,])

    # print(labels_train.shape, labels_test.shape)

    print("begin saving...",end='\r')
    np.savez_compressed(save_path + "train_input_{}.npz".format(pack), 
        inputs=[data[0] for data in results[:int(l_r*4/5)]])
    np.savez_compressed(save_path + "train_mask_{}.npz".format(pack), 
        masks=[data[1] for data in results[:int(l_r*4/5)]])
    np.savez_compressed(save_path + "train_label_{}.npz".format(pack), 
        labels=labels_train)

    np.savez_compressed(save_path + "test_input_{}.npz".format(pack), 
        inputs=[data[0] for data in results[int(l_r*4/5):]])
    np.savez_compressed(save_path + "test_mask_{}.npz".format(pack), 
        masks=[data[1] for data in results[int(l_r*4/5):]])
    np.savez_compressed(save_path + "test_label_{}.npz".format(pack), 
        labels=labels_test)
    print("saved data, pack: ",pack)


if __name__ == "__main__":
    print("begin processing...")
    st = time()
    save_path = "/gl_data/"
    base_path = "/dataset/"
    path_child = [base_path + i for i in os.listdir(base_path)]
    path_leaf = []
    for i in path_child:
        if "zip" in i: continue
        path_leaf += [i + "/" + j for j in os.listdir(i)]
    shuffle(path_leaf)
    # data = json.load(file)[:8]
    data = path_leaf
    data_len = len(data)
    print("data-len: ",data_len)
    results = []
    pack = 0
    size = 1000

    print("time = %d min %d s" % (int(time() - st) / 60, (time() - st) % 60))
    pool = mp.Pool(64)
    if data_len > size:
        for p in range(0,data_len,size):
            if p + size < data_len: child = data[p:p+size]
            else: child = data[p:]
            result_ = list(pool.map(build,child))
            for res in result_:
                results.extend(res)
            if result_:
                pack += 1
                save(results, pack)
                print("time = %d min %d s" % (int(time() - st) / 60, (time() - st) % 60))

            result_ = []
            results = []
            del child
            collect()
    else:
        result_ = list(64)
        for res in result_:
            results.extend(res)
        
        if result_:
            pack += 1
            save(results, pack)
            print("time = %d min %d s" % (int(time() - st) / 60, (time() - st) % 60))
        results = []
        result_ = []
        collect()

    pool.close()
    # pool.join()
    file.close()
 

# datas,legals,labels = build('E:\\CodePalace\\cpp code\\AI-game\\Generals.io_crawl\\dataset\\json\\json1\\ruwQa4Wmq.json')



