import sys,torch
from click import get_app_dir
# sys.path.append("E:\CodePalace\cpp code\AI-game\Magic-generals")
from adapter import Adapter
from copy import deepcopy
import torch, torch.nn as nn
from torch.nn.functional import softmax

# from AI_model import gl_model

def in_map(i, j):
    return (
        i>=0 and i<=24
        and j>=0 and j<=24
    )

@torch.no_grad()
def AIbot(k,length,width,visual_field_list,turn,model):
    cross_map = {
        25*11+12: 0,
        25*13+12: 1,
        25*12+11: 2,
        25*12+13: 3,
    }
    d_ij = [
        [-1,1,0,0],
        [0,0,-1,1],
    ]
    cross_mask_4 = [
        (0,11,12),
        (0,13,12),
        (0,12,11),
        (0,12,13),
    ]
    cross_mask = torch.zeros((1,25,25))
    for i in cross_mask_4:
        cross_mask[i] = 1
    # cross_mask[(0,12,11)],cross_mask[(0,12,13)],cross_mask[(0,11,12)],cross_mask[(0,13,12)] = 1,1,1,1
    data, mask__ = Adapter(deepcopy(visual_field_list), k, turn)

    output_ = model(torch.from_numpy(data).unsqueeze(0).float()).detach()
    output_ = output_.reshape([2,25,25])
    mask_ = mask__.reshape([1,25,25])
    output_L1_ = output_[0].clone()
    output_L1 = torch.mul(output_L1_,torch.from_numpy(mask_))
    
    # print(output_L1.shape)
    output_L1 = output_L1.reshape([625,])
    ans_ = torch.argmax(softmax(output_L1, dim = -1), dim=-1)
    ans_ = [int(ans_/25), int(ans_%25)]
    time = 0
    print("beg")
    print(ans_)
    for i in range(4):
        cross_mask[cross_mask_4[i]] = 0
        if in_map(ans_[0]+d_ij[0][i],ans_[1]+d_ij[1][i]):
            if (data[7][ans_[0]+d_ij[0][i]][ans_[1]+d_ij[1][i]] == 0):
                cross_mask[cross_mask_4[i]] = 1
                print(i)
    print("end")
    
    mask = torch.cat([torch.from_numpy(mask_), cross_mask], dim=-3)
    output = torch.mul(output_, mask).reshape([2,625])
    ans = torch.argmax(softmax(output,dim = -1), dim=-1)

    if int(ans[1]) not in [25*11+12,25*12+11,25*12+13,25*13+12]:
        # raise ValueError("Error ans: ",ans)
        return []
    ans = [int(ans[0]), int(ans[1])]
    ans1 = cross_map[ans[1]]
    ans0 = [int(ans[0]/25), ans[0]%25]
    # print([*ans0, 0, ans1])
    return [*ans0, 0, ans1]

    

# if __name__ == '__main__':

