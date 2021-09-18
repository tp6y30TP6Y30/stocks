import requests
from time import sleep
import pandas as pd
from io import StringIO
from tqdm import tqdm
import os
from os.path import join
from os import listdir
import matplotlib.pyplot as plt
import numpy as np
import default_config as config

# MarginTradingShortSelling:
# https://www.twse.com.tw/exchangeReport/MI_MARGN?response=html&selectType=ALL&date=20210827&yy=2021&mm=8&dd=27

def getDailyStocks(date):
	address = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date + '&type=ALL'
	request = requests.post(address)
	sleep(3)
	dailyStocks = pd.read_csv(StringIO(request.text.replace("=", "")), header = ["證券代號" in content for content in request.text.split("\n")].index(True) - 1)
	dailyStocks['成交股數'] = dailyStocks['成交股數'].apply(lambda content: content.replace(",", ""))
	dailyStocks['成交筆數'] = dailyStocks['成交筆數'].apply(lambda content: content.replace(",", ""))
	dailyStocks['成交金額'] = dailyStocks['成交金額'].apply(lambda content: content.replace(",", ""))
	# dailyStocks = dailyStocks[pd.to_numeric(dailyStocks['本益比'], errors='coerce') < 3]
	# print(dailyStocks)
	filename = date
	return dailyStocks, filename

def getRangeStocks(save_dir, start_year, due_year):
	years = [str(year).zfill(4) for year in range(start_year, due_year + 1)]
	months = [str(month).zfill(2) for month in range(1, 13)]
	days = [str(day).zfill(2) for day in range(1, 32)]
	for year in years:
		for month in tqdm(months, ncols = 70, desc = '{}/{}'.format(year, years[-1])):
			for day in days:
				try:
					date = year + month + day
					dailyStocks, filename = getDailyStocks(date)
					dailyStocks.to_csv(join(save_dir, filename), encoding = 'utf-8-sig')
				except ValueError:
					pass

def getStocks(save_dir, start_year, due_year):
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)
		getRangeStocks(save_dir, start_year, due_year)
	else:
		print('getStocks: save_dir already exists!')

def getDailyInvestors(date):
	address = 'https://www.twse.com.tw/fund/T86?response=csv&date=' + date + '&selectType=ALL'
	request = requests.post(address)
	sleep(3)
	dailyInvestors = pd.read_csv(StringIO(request.text.replace("=", "")), header = ["證券代號" in content for content in request.text.split("\n")].index(True))
	startRemoveIndex = dailyInvestors[dailyInvestors["證券代號"] == "說明:"].index[0]
	dailyInvestors = dailyInvestors.iloc[:startRemoveIndex]
	dailyInvestors['三大法人買賣超股數'] = dailyInvestors['三大法人買賣超股數'].apply(lambda content: str(content).replace(",", ""))
	filename = date
	return dailyInvestors, filename

def getRangeInvestors(save_dir, start_year, due_year):
	years = [str(year).zfill(4) for year in range(start_year, due_year + 1)]
	months = [str(month).zfill(2) for month in range(1, 13)]
	days = [str(day).zfill(2) for day in range(1, 32)]
	for year in years:
		for month in tqdm(months, ncols = 70, desc = '{}/{}'.format(year, years[-1])):
			for day in days:
				try:
					date = year + month + day
					dailyInvestors, filename = getDailyInvestors(date)
					dailyInvestors.to_csv(join(save_dir, filename), encoding = 'utf-8-sig')
				except ValueError:
					pass

def getInvestors(save_dir, start_year, due_year):
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)
		getRangeInvestors(save_dir, start_year, due_year)
	else:
		print('getInvestors: save_dir already exists!')

def getMatchDates(stocks_dir, investors_dir):
	stocks_ptr, investors_ptr = 0, 0
	stocks_dates, investors_dates = listdir(stocks_dir), listdir(investors_dir)
	matchDates = []
	while True:
		if stocks_ptr == len(stocks_dates) and investors_ptr == len(investors_dates):
			break
		elif stocks_ptr == len(stocks_dates):
			investors_ptr += 1
		elif investors_ptr == len(investors_dates):
			stocks_ptr += 1
		elif stocks_dates[stocks_ptr] == investors_dates[investors_ptr]:
			matchDates.append(stocks_dates[stocks_ptr])
			stocks_ptr += 1
			investors_ptr += 1
		elif stocks_dates[stocks_ptr] < investors_dates[investors_ptr]:
			stocks_ptr += 1
		else:
			investors_ptr += 1
	return matchDates

def getHistorys(stocks_dir, investors_dir, selectStocks, matchDates):
	dates = matchDates
	rows = ['open', 'high', 'low', 'close', 'investors']
	historys = {selectStock: pd.DataFrame([], columns = dates, index = rows) for selectStock in selectStocks}
	for date in tqdm(dates, ncols = 70, desc = 'Processing Data'):
		stocks_filepath = join(stocks_dir, date)
		investors_filepath = join(investors_dir, date)
		dailyStocks = pd.read_csv(stocks_filepath)
		dailyInvestors = pd.read_csv(investors_filepath)
		for selectStock in selectStocks:
			selectDailyStocks = dailyStocks[dailyStocks["證券代號"] == selectStock]
			selectDailyInvestors = dailyInvestors[dailyInvestors["證券代號"] == selectStock]
			selectStockExist = len(selectDailyStocks) > 0 and len(selectDailyInvestors) > 0
			if selectStockExist:
				open, high, low, close = selectDailyStocks["開盤價"].iloc[0], selectDailyStocks["最高價"].iloc[0], selectDailyStocks["最低價"].iloc[0], selectDailyStocks["收盤價"].iloc[0]
				investors = selectDailyInvestors["三大法人買賣超股數"].iloc[0]
				historys[selectStock].loc['open', date]      = open
				historys[selectStock].loc['high', date]      = high
				historys[selectStock].loc['low',  date]      = low
				historys[selectStock].loc['close', date]     = close
				historys[selectStock].loc['investors', date] = investors
	return historys

def arrangeSelectStocks(stocks_dir, investors_dir, save_dir, selectStocks, matchDates):
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)
		historys = getHistorys(stocks_dir, investors_dir, selectStocks, matchDates)
		for selectStock in selectStocks:
			historys[selectStock].to_csv(join(save_dir, selectStock))
	else:
		print('arrangeSelectStocks: save_dir already exists!')

def containMissingData(history):
	return history.isnull().values.any()

def handleMissingDate(load_dir, save_dir):
	selectStocks = listdir(load_dir)
	historys = {selectStock: pd.read_csv(join(load_dir, selectStock), index_col = 0) for selectStock in selectStocks}
	for selectStock in tqdm(selectStocks, ncols = 70, desc = 'Pruning Data'):
		historys[selectStock] = historys[selectStock].apply(lambda value: pd.to_numeric(value, errors = 'coerce'))
		dates = historys[selectStock].columns
		for date in dates:
			if containMissingData(historys[selectStock].iloc[:][date]):
				historys[selectStock] = historys[selectStock].drop(date, axis = 1)
			else:
				break
	for selectStock in selectStocks:
		filename = selectStock + ('_error' if containMissingData(historys[selectStock]) else '')
		historys[selectStock].to_csv(join(save_dir, filename))

def dataPruning(load_dir, save_dir):
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)
		handleMissingDate(load_dir, save_dir)
	else:
		print('dataPruning: save_dir already exists!')

if __name__ == '__main__':
	getStocks(save_dir = config.rawStocks_dir, start_year = config.start_year, due_year = config.due_year)
	getInvestors(save_dir = config.rawInvestors_dir, start_year = config.start_year, due_year = config.due_year)
	matchDates = getMatchDates(stocks_dir = config.rawStocks_dir, investors_dir = config.rawInvestors_dir)
	arrangeSelectStocks(stocks_dir = config.rawStocks_dir, investors_dir = config.rawInvestors_dir, save_dir = config.selectStocks_dir, selectStocks = config.selectStocks, matchDates = matchDates)
	dataPruning(load_dir = config.selectStocks_dir, save_dir = config.prunedData_dir)