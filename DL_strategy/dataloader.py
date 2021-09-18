import pandas as pd
import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import numpy as np

class StockData(Dataset):
    def __init__(self, datapath, duration, mode, start_index, last_index):
        super(StockData, self).__init__()
        self.mode = mode
        self.transform = transforms.Compose([
                            transforms.ToTensor(),
                         ])
        self.data = pd.read_csv(datapath, index_col = 0).values.transpose()[start_index:last_index] if mode == 'train' else pd.read_csv(datapath, index_col = 0).values.transpose()[start_index:]
        self.duration = duration
        self.label = [label * 1.0 for label in (self.data[1:] - self.data[0:-1])[:, -2] >= 0]

    def __len__(self):
        return self.data.shape[0] - self.duration - 1

    def __getitem__(self, index):
        duration_stocks = self.transform(self.data[index:index + self.duration]).reshape(-1).float()
        duration_action = self.label[index + self.duration - 1]
        return duration_stocks, duration_action

if __name__ == '__main__':
    dataset = StockData('../data/prunedData/0050', 20, 'valid', 0, -1)
    loader = DataLoader(dataset, batch_size = 16, shuffle = True)
    for duration_stocks, duration_action in tqdm(loader, ncols = 70):
        print(duration_stocks.shape)
        print(duration_action.shape)
        break