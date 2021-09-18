datapath = '../data/prunedData/0050'
strategy_chosen = 1

if strategy_chosen == 0:
    days_a = [d for d in range(0, 10, 2)]
    days_b = [d for d in range(10, 20, 2)]
    days_c = [d for d in range(20, 40, 2)]
    days_d = [d for d in range(40, 60, 2)]
    action_a = [-1, 1]
    action_b = [-1, 1]

elif strategy_chosen == 1:
    days = [day for day in range(5, 20, 2)]
    KD_upbound = [up for up in range(50, 100, 10)]
    KD_lowbound = [low for low in range(0, 50, 10)]
    keepDays = [day for day in range(3, 10, 2)]

elif strategy_chosen == 2:
    RSI_upbound = [up for up in range(50, 100, 10)]
    RSI_lowbound = [low for low in range(0, 50, 10)]
    long = [day for day in range(20, 60, 5)]
    short = [day for day in range(3, 30, 5)]
    cross_w = [w / 10 for w in range(0, 11)]
    RSI_w = [w / 10 for w in range(0, 11)]
    threshold = [th / 10 for th in range(0, 21, 2)]

elif strategy_chosen == 3:
    long = [day for day in range(20, 60, 5)]
    short = [day for day in range(3, 30, 5)]
    days = [day for day in range(5, 20, 2)]
    threshold = [th / 10 for th in range(0, 50, 5)]

