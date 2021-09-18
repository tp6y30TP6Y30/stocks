import os
from os.path import join
from predictor import StocksPredictor
from dataloader import StockData
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description = 'Setup the training settings.',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--datapath', default = '../data/prunedData/0050',
                        help = "The directory that contains data files")

    parser.add_argument('--test', action = 'store_true',
                        help = "test mode or others (train, valid)")

    parser.add_argument('--save-path', default = './models/', type = str,
                        help = "The directory that restores the model")

    parser.add_argument('--duration', default = 100, type = int,
                        help = "The duration days of the stocks")

    parser.add_argument('--epochs', default = 100, type = int,
                        help = "The total training epochs")

    parser.add_argument('--batchsize', default = 64, type = int,
                        help = "The training batchsize")

    parser.add_argument('--lr', default = 1e-3, type = float,
                        help = "The training learning rate")

    args = parser.parse_args()
    return args

def train(dataset, model, device, optimizer, criterion, args, epoch, epochs):
    dataloader = DataLoader(dataset, batch_size = args.batchsize, shuffle = True, num_workers = 4, pin_memory = True)
    model.train()
    loss_data = 0
    for duration_stocks, duration_action in tqdm(dataloader, ncols = 70, desc = '[Train] {:d}/{:d}'.format(epoch, epochs)):
        duration_stocks, duration_action = duration_stocks.to(device), duration_action.to(device)
        optimizer.zero_grad()
        pred_action = model(duration_stocks)
        loss = criterion(pred_action.double(), duration_action.double())
        loss.backward()
        loss_data += loss.item()
        optimizer.step()
    print('classify loss: ', loss_data / len(dataloader))

def valid(dataset, model, device, optimizer, criterion, args, epoch, epochs):
    dataloader = DataLoader(dataset, batch_size = args.batchsize, shuffle = True, num_workers = 4, pin_memory = True)
    model.eval()
    loss_data = 0
    with torch.no_grad():
        for duration_stocks, duration_action in tqdm(dataloader, ncols = 70, desc = '[Valid] {:d}/{:d}'.format(epoch, epochs)):
            duration_stocks, duration_action = duration_stocks.to(device), duration_action.to(device)
            pred_action = model(duration_stocks)
            loss = criterion(pred_action.double(), duration_action.double())
            loss_data += loss.item()
    print('classify loss: ', loss_data / len(dataloader))
    print()

def main():
    args = parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    os.makedirs(args.save_path, exist_ok = True)
    train_dataset = StockData(args.datapath, args.duration, mode = 'train', start_index = 0, last_index = -200)
    valid_dataset = StockData(args.datapath, args.duration, mode = 'valid', start_index = -200, last_index = -1)
    model = StocksPredictor(in_channels = args.duration * 5).to(device).float()
    optimizer = torch.optim.SGD(filter(lambda param : param.requires_grad, model.parameters()), lr = args.lr, momentum = 0.9)   
    criterion = nn.BCELoss().to(device).float()
    for epoch in range(1, args.epochs + 1):
        train(train_dataset, model, device, optimizer, criterion, args, epoch, args.epochs)
        valid(valid_dataset, model, device, optimizer, criterion, args, epoch, args.epochs)
        if epoch % 5 == 0: torch.save(model.state_dict(), args.save_path + '{}.ckpt'.format(epoch))

if __name__ == '__main__':
    torch.multiprocessing.freeze_support()
    main()