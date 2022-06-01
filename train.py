from audioop import cross
from os.path import exists
from random import sample
from time import time
from gc import collect
from numpy import arange, load
import torch, torch.nn as nn
from torch.nn.functional import softmax
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import Dataset, DataLoader
from prefetch_generator import BackgroundGenerator
import sys,os,requests

lr = 4e-4
batch = 1024
epoch = 48
rep = (100,50)


torch.backends.cudnn.benchmark = True

class resblock(nn.Module):
    def __init__(self, channel: int) -> None:
        super(resblock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(channel, channel, (3,3), padding=(1,1), bias=True), 
            nn.BatchNorm2d(channel),
            nn.Conv2d(channel, channel, (3,3), padding=(1,1), bias=True), 
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
            # nn.BatchNorm2d(24),
            nn.Conv2d(24, 12, (3,3), padding=(1,1), bias=True),
            nn.ReLU(True),
            # nn.BatchNorm2d(8),
            *[resblock(12) for i in range(12)],
            nn.Conv2d(12, 2, (1,1), padding=(0,0), bias=True),
            nn.ReLU(True),
        )
    def forward(self,x):
        return self.net(x)


class dataset(Dataset):
    idxs = range(1,33)
    def __init__(self, state: str):
        
        super(dataset, self).__init__()
        local_path = "/gldata/{}_".format(state)
        self.inputs, self.masks, self.labels = [],[],[]
        choose = sample(dataset.idxs, 4)
        print("pack", end = ' ')
        for k in choose:
            print(k, end = ' ')
            self.inputs.extend([torch.from_numpy(f) for f in 
                load(local_path + "input_{}.npz".format(k), allow_pickle=True)['inputs'] ])
            self.masks.extend([torch.from_numpy(f) for f in 
                load(local_path + "mask_{}.npz".format(k), allow_pickle=True)['masks'] ])
            self.labels.extend([torch.from_numpy(f) for f in 
                load(local_path + "label_{}.npz".format(k), allow_pickle=True)['labels'] ])
        self.len = len(self.labels)
        assert len(self.labels) == len(self.inputs), "data error[0]"
        assert len(self.labels) == len(self.masks), "data error[1]"
        message = "{} sample = {}".format(state, self.len)
        print('\n'+message), 
        # file.write(message+"\n")
    def __getitem__(self, index):
        return self.inputs[index],self.masks[index],self.labels[index]
    
    def __len__(self):
        return self.len

class Loader(DataLoader):
    def __iter__(self):
        return BackgroundGenerator(super().__iter__())



def training(train):
    print("train batch num=",len(train))
    acc, avaloss = 0.0, 0.0
    for i, sample in enumerate(train, 1):
        model.train()
        optimizer.zero_grad()
        inputs, masks, labels = sample
        inputs = inputs.cuda().float()
        masks = masks.cuda().float()
        labels = labels.cuda().float()
        output = model(inputs)
        output_shape = list(output.shape)
        o1_ = torch.mul(output[:,0,:,:], masks)
        o1 = o1_.reshape([output_shape[0],1,25,25])
        o2_ = torch.mul(output[:,1,:,:], cross_mask)
        o2 = o2_.reshape([output_shape[0],1,25,25])
        output = torch.cat([o1,o2],dim = -3).requires_grad_(True)
        output_shape = list(output.shape)
        output = output.reshape(output_shape[:-2]+[25*25,])
        ans = torch.argmax(softmax(output,dim = -1), dim=-1)
        loss = lossfunc(output, labels)
        loss.requires_grad_(True)
        loss.backward()
        # print(list(model.children())[0].weight.grad)
        # print([x.grad for x in optimizer.param_groups[0]['params']])
        # print(model.net[0].weight.grad)

        # for name, parms in model.named_parameters(): 
        #     print('-->name:', name, '-->grad_requirs:',parms.requires_grad, ' -->grad_value:',parms.grad)
        #     a = input(":")

        # a = input(":")
        optimizer.step()
        avaloss += loss.item()
        labels = torch.argmax(labels, dim=-1)
        acc += (ans == labels).sum().item()
        
        torch.cuda.empty_cache()
        if not i % rep[0]:
            avaloss /= rep[0]
            acc *= 100 / rep[0] / batch
            s = "[Epoch %2d, Data %4d] loss = %.2e acc = %2.2f%% lr = %.0e" % \
                (k, i, avaloss, acc, optimizer.param_groups[0]["lr"])
            print(s), file.write(s + "\n")
            avaloss, acc = 0.0, 0

def testing(test):
    print("test batch num =", len(test))
    allacc, acc, allloss, avaloss = 0, 0, 0.0, 0.0
    with torch.no_grad():
        for i, sample in enumerate(test, 1):
            inputs, masks, labels = sample
            inputs = inputs.cuda().float()
            masks = masks.cuda().float()
            labels = labels.cuda().float()
            output = model(inputs)
            output_shape = list(output.shape)
            o1 = torch.mul(output[:,0,:,:], masks).reshape([output_shape[0],1,25,25])
            o2 = torch.mul(output[:,1,:,:], cross_mask).reshape([output_shape[0],1,25,25])
            output = torch.cat([o1,o2],dim = -3)
            output_shape = list(output.shape)
            output = output.reshape(output_shape[:-2]+[25*25,])
            ans = torch.argmax(softmax(output,dim = -1), dim=-1)
            loss = lossfunc(output, labels)
            avaloss += loss.item()
            labels = torch.argmax(labels, dim=-1)
            acc += (ans == labels).sum().item()
            torch.cuda.empty_cache()
            if not i % rep[1]:
                allacc += acc
                allloss += avaloss
                s = "%3d loss = %.2e, acc = %.2f%%" % \
                    (i, avaloss / rep[1], 100 * acc / rep[1] / batch)
                print(s,end="\n"), file.write(s + "\n")
                acc, avaloss = 0, 0.0
        allacc += acc
        allloss += avaloss
    s = "avaloss = %.2e, total acc = %.2f%%" %\
         (allloss / len(test), 100 * allacc / len(test) / batch)
    print(s+'\n'), file.write(s + "\n")


if __name__ == '__main__':
    file = open("./gl.txt", "a+")
    dst = "./gl.pth"
    cross_mask = torch.zeros((25,25)).cuda()
    cross_mask[(12,11)],cross_mask[(12,13)],cross_mask[(11,12)],cross_mask[(13,12)] = 1,1,1,1
    cross_mask.requires_grad_(True)
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
    lossfunc.requires_grad_(True)
    if trained < epoch:
        print("training starting....")
        st = time()
        for k in range(trained + 1, epoch + 1):
            s = "Epoch {}".format(k)
            print(s), file.write(s+'\n')
            training(Loader(dataset("train"), batch, True))
            testing(Loader(dataset("test"), batch))
            scheduler.step()
            torch.cuda.empty_cache()
            state = {"net": model.state_dict(), "optim": optimizer.state_dict(), 
                "sch": scheduler.state_dict(), "epoch": k}
            torch.save(state, dst)
            print("model saved after %d epoch" % k)
            print("time = %d h %d min %d s\n" % (int((time() - st) / 3600), 
                (int(time() - st) / 60) % 60, (time() - st) % 60))
            file.flush()
    file.close() 