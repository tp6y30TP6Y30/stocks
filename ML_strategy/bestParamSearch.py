import default_config as config
import pandas as pd
import numpy as np
from tqdm import tqdm
import strategy

def calTotalIter(*args):
	totalIter = 1
	for i in args:
		totalIter *= len(i)
	return totalIter

def computeReturnRate(strategy, *args):
	capital = 10000.0
	capitalOrig = capital
	transFeeRate = 0.001425
	evalDays = 30
	action = np.zeros((evalDays, 1))
	realAction = np.zeros((evalDays, 1))
	total = np.zeros((evalDays, 1))
	total[0] = capital
	Holding = 0.0
	openPricev = data.loc["open"][-evalDays:]

	for ic in range(evalDays, 0, -1):
		dataFile = data.iloc[:, len(data.columns)-ic:]
		action[evalDays - ic] = strategy(*args)
		currPrice = openPricev[evalDays - ic]
		if action[evalDays - ic] == 1:
			transFee = transFeeRate * capital if transFeeRate * capital > 20.0 else 20.0
			if Holding == 0 and capital > transFee:
				Holding = (capital - transFee) / currPrice
				capital = 0
				realAction[evalDays - ic] = 1
		elif action[evalDays - ic] == -1:
			transFee = transFeeRate * Holding * currPrice
			if Holding > 0 and Holding * currPrice > transFee:
				capital = Holding * currPrice - transFee
				Holding = 0
				realAction[evalDays-ic] = -1

		transFee = transFeeRate * Holding * currPrice
		total[evalDays - ic] = capital + float(Holding > 0) * (Holding * currPrice - transFee)

	returnRate = (total[-1] - capitalOrig) / capitalOrig
	return returnRate

if __name__=='__main__':
	bestReturnRate = -1.00
	data = pd.read_csv(config.datapath, index_col = 0)
	strategies = [strategy.movingAverageIndicator, strategy.KDIndicator, strategy.RSIIndicator, strategy.MACDIndicator]
	strategy = strategies[config.strategy_chosen]
	count = 0
	if config.strategy_chosen == 0:
		total_iter = calTotalIter(config.days_a, config.days_b, config.days_c, config.days_d, config.action_a, config.action_b)
		for da in config.days_a:
			for db in config.days_b:
				for dc in config.days_c:
					for dd in config.days_d:
						for aa in config.action_a:
							for ab in config.action_b:
								days, actions = [da, db, dc, dd], [aa, ab]
								if count % 100 == 0: print('[Process: {:.4f}%] Current settings: '.format(count / total_iter * 100), days, actions)
								count += 1
								returnRate = computeReturnRate(strategy, data, days, actions)
								if returnRate > bestReturnRate:
									bestReturnRate = returnRate
									bestDays = days
									bestActions = actions
									print('Best settings: ', bestDays, bestActions)
									print('Best return rate:', bestReturnRate[0] * 100, '%')
									print()
	elif config.strategy_chosen == 1:
		total_iter = calTotalIter(config.days, config.KD_upbound, config.KD_lowbound, config.keepDays)
		for d in config.days:
			for up in config.KD_upbound:
				for low in config.KD_lowbound:
					for keep in config.keepDays:
						days, KD_upbound, KD_lowbound, keepDays = d, up, low, keep
						if count % 100 == 0: print('[Process: {:.4f}%] Current settings: '.format(count / total_iter * 100), days, KD_upbound, KD_lowbound, keepDays)
						count += 1
						returnRate = computeReturnRate(strategy, data, days, KD_upbound, KD_lowbound, keepDays)
						if returnRate > bestReturnRate:
							bestReturnRate = returnRate
							bestDays = days
							bestKD_upbound = KD_upbound
							bestKD_lowbound = KD_lowbound
							bestKeepDays = keepDays
							print('Best settings: ', bestDays, bestKD_upbound, bestKD_lowbound, bestKeepDays)
							print('Best return rate:', bestReturnRate[0] * 100, '%')
							print()
	elif config.strategy_chosen == 2:
		total_iter = calTotalIter(config.RSI_upbound, config.RSI_lowbound, config.long, config.short, config.cross_w, config.RSI_w, config.threshold)
		for up in config.RSI_upbound:
			for low in config.RSI_lowbound:
				for l in config.long:
					for s in config.short:
						for c in config.cross_w:
							for rsi in config.RSI_w:
								for th in config.threshold:
									RSI_upbound, RSI_lowbound, long, short, cross_w, RSI_w, threshold = up, low, l, s, c, rsi, th
									if count % 100 == 0: print('[Process: {:.4f}%] Current settings: '.format(count / total_iter * 100), RSI_upbound, RSI_lowbound, long, short, cross_w, RSI_w, threshold)
									count += 1
									returnRate = computeReturnRate(strategy, data, RSI_upbound, RSI_lowbound, long, short, cross_w, RSI_w, threshold)
									if returnRate > bestReturnRate:
										bestReturnRate = returnRate
										bestRSI_upbound = RSI_upbound
										bestRSI_lowbound = RSI_lowbound
										bestLong = long
										bestShort = short
										bestCross_w = cross_w
										bestRSI_w = RSI_w
										bestThreshold = threshold
										print('Best settings: ', bestRSI_upbound, bestRSI_lowbound, bestLong, bestShort, bestCross_w, bestRSI_w, bestThreshold)
										print('Best return rate:', bestReturnRate[0] * 100, '%')
										print()
	elif config.strategy_chosen == 3:
		total_iter = calTotalIter(config.long, config.short, config.days, config.threshold)
		for l in config.long:
			for s in config.short:
				for d in config.days:
					for th in config.threshold:
						long, short, days, threshold = l, s, d, th
						if count % 100 == 0: print('[Process: {:.4f}%] Current settings: '.format(count / total_iter * 100), long, short, days, threshold)
						count += 1
						returnRate = computeReturnRate(strategy, data, long, short, days, threshold)
						if returnRate > bestReturnRate:
							bestReturnRate = returnRate
							bestLong = long
							bestShort = short
							bestDays = days
							bestThreshold = threshold
							print('Best settings: ', bestLong, bestShort, bestDays, bestThreshold)
							print('Best return rate:', bestReturnRate[0] * 100, '%')
							print()