import torch, torch.nn as nn

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


