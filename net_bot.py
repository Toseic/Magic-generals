import sys,torch
# sys.path.append("E:\CodePalace\cpp code\AI-game\Magic-generals")
from adapter import Adapter
from copy import deepcopy
import torch, torch.nn as nn
from torch.nn.functional import softmax

# from AI_model import gl_model



@torch.no_grad()
def AIbot(k,length,width,visual_field_list,turn,model):
    cross_map = {
        25*11+12: 0,
        25*13+12: 3,
        25*12+11: 1,
        25*12+13: 2,
    }
    cross_mask = torch.zeros((1,25,25))
    cross_mask[(0,12,11)],cross_mask[(0,12,13)],cross_mask[(0,11,12)],cross_mask[(0,13,12)] = 1,1,1,1
    data, mask__ = Adapter(deepcopy(visual_field_list), k, turn)

    output_ = model(torch.from_numpy(data).unsqueeze(0).float()).detach()
    output_.reshape([2,25,25])
    mask_ = mask__.reshape([1,25,25])
    mask = torch.cat([torch.from_numpy(mask_), cross_mask], dim=-3)
    output = torch.mul(output_, mask).reshape([2,625])
    ans = torch.argmax(softmax(output,dim = -1), dim=-1)
    if int(ans[1]) not in [25*11+12,25*12+11,25*12+13,25*13+12]:
        raise ValueError("Error ans: ",ans)
    ans = [int(ans[0]), int(ans[1])]
    ans1 = cross_map[ans[1]]
    ans0 = [int(ans[0]/25), ans[0]%25]

    return [*ans0, 0, ans1]

    

# if __name__ == '__main__':

