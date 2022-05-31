from audioop import cross
from os.path import exists
from random import sample
from time import time
from gc import collect
from numpy import load
import torch, torch.nn as nn
from torch.nn.functional import softmax
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import Dataset, DataLoader
from prefetch_generator import BackgroundGenerator
import sys,os,requests

lr = 4e-4
batch = 480
epoch = 12
rep = (100,50)


torch.backends.cudnn.benchmark = True

class resblock(nn.Module):
    def __init__(self, channel: int) -> None:
        super(resblock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(channel, channel, (3,3), padding=(1,1), bias=False), 
            nn.BatchNorm2d(channel),
            nn.Conv2d(channel, channel, (3,3), padding=(1,1), bias=False), 
            nn.BatchNorm2d(channel),
        )
        self.act = nn.ReLU(True)

    def forward(self, x):
        y = self.conv(x)
        return self.act(x + y)

class gl_model(nn.Module):
    def __init__(self) -> None:
        super(gl_model, self).__init__()
        self.net = nn.Sequential(
            nn.Conv2d(10, 24, (3,3), padding=(1,1), bias=True), 
            nn.BatchNorm2d(24),
            nn.Conv2d(24, 8, (3,3), padding=(1,1), bias=True),
            nn.ReLU(True),
            nn.BatchNorm2d(8),
            *[resblock(8) for i in range(8)],
            nn.Conv2d(8, 2, (1,1), padding=(0,0), bias=True),
            nn.ReLU(True),
        )
    def forward(self,x):
        return self.net(x)


class dataset(Dataset):
    idxs = []
    def __init__(self, state: str) -> None:
        super(dataset, self).__init__()
        local_path = "/dataset/{}_".format(state)
        self.inputs, self.masks, self.labels = [],[],[]
        choose = sample(dataset.idxs, 1)
        print("pack", end = ' ')
        for k in choose:
            print(k, end = ' ')
            self.inputs.extend([torch.from_numpy(f) for f in 
                load(local_path + "input_{}.npz".format(k)) ])
            self.masks.extend([torch.from_numpy(f) for f in 
                load(local_path + "mask_{}.npz".format(k)) ])
            self.labels.extend([torch.from_numpy(f) for f in 
                load(local_path + "label_{}.npz".format(k)) ])
        self.len = len(self.labels)
        assert len(self.labels) == len(self.inputs), "data error[0]"
        assert len(self.labels) == len(self.masks), "data error[1]"
        message = "{} sample = {}".format(state, self.len)
        print(message), 
        # file.write(message+"\n")
    def __getitem__(self, index):
        return self.inputs[index],self.masks[index],self.labels[index]
    
    def __len__(self):
        return self.len

class Loader(DataLoader):
    def __iter__(self):
        return BackgroundGenerator(super().__iter__())

def softmax_(ten: torch.Tensor):
	shape_ = list(ten.shape)
	ten = ten.reshape(tuple(shape_[:-2]+[shape_[-1]*shape_[-2],]))
	ten = softmax(ten, dim = -1)
	ten = ten.reshape(shape_)

def training(train):
    print("train batch num=",len(train))
    acc, avaloss = 0.0, 0.0
    for i, sample in enumerate(train, 1):
        model.train()
        optimizer.zero_grad()
        inputs, masks, labels = sample
        inputs = inputs.cuda().float()
        masks = masks.cuda().float()
        labels = labels.cuda().flaot()
        output = model(inputs)
        output[:,0,:,:] = torch.mul(output[:,0,:,:], masks)
        output[:,1,:,:] = torch.mul(output[:,1,:,:], cross_mask)
        output_shape = output.shape
        output = output.reshape(output_shape[:-2]+[25*25,]).detach()
        ans = torch.argmax(softmax(output,dim = -1), dim=-1)
        loss = lossfunc(output, labels)
        
        # point: mask? killed?  TODO




if __name__ == '__main__':
    file = open("./gl.txt", "a+")
    dst = "./gl.pth"
    cross_mask = torch.zeros((25,25))
    cross_mask[(12,11)],cross_mask[(12,13)],cross_mask[(11,12)],cross_mask[(13,12)] = 1,1,1,1
    model = gl_model().cuda()
    optimizer = AdamW(model.parameters(), lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, 5, 1e-6)
    if exists(dst):
        saved = torch.load(dst)
        model.load_state_dict(saved["net"])
        optimizer.load_state_dict(saved["optim"])
        scheduler.load_state_dict(saved["sch"])
        trained = saved["epoch"] if "epoch" in saved else 0
    else:
        trained = 0
    lossfunc = nn.CrossEntropyLoss()
    if trained < epoch:
        print("trainint starting....")
        st = time()
        for k in range(trained + 1, epoch + 1):
            s = "Epoch {}".format(k)
            print(s), file.write(s+'\n')
            training(Loader(dataset("train"), batch, True))
