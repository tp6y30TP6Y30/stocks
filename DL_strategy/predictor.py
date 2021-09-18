import torch
import torch.nn as nn

def weights_init_uniform(m):
    classname = m.__class__.__name__
    # for every Linear layer in a model..
    if classname.find('Linear') != -1:
        # apply a uniform distribution to the weights and a bias=0
        m.weight.data.uniform_(0.0, 1.0)
        m.bias.data.fill_(0)

class StocksPredictor(nn.Module):
    def __init__(self, in_channels, out_channels = 1):
        super(StocksPredictor, self).__init__()
        self.linear = nn.Sequential(
                        nn.Linear(in_channels, in_channels * 2),
                        nn.BatchNorm1d(in_channels * 2),
                        nn.ReLU(True),
                        nn.Linear(in_channels * 2, out_channels),
                        nn.Sigmoid()
                      )
        weights_init_uniform(self.linear)

    def forward(self, x):
        return self.linear(x).squeeze(-1)