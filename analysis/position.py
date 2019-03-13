import numpy as np
import pandas as pd


# if long and short instrument are different
def position_one_market(long, short, tr_cap, pvt):
    # tr_cap: trade capital, pvt: percentage volatility target
    # annualised cash target volatility
    actv = tr_cap * pvt
    # daily cash target volatility
    dctv = actv / 16

    long_pos = position_one_direction(long, dctv)
    short_pos = position_one_direction(short, dctv)

    agg = pd.DataFrame(index=long_pos.index.values)
    for col in long_pos.columns:
        agg['long_' + col] = long_pos[col]
        agg['short_' + col] = short_pos[col]

    for col in long_pos.columns:
        agg.loc[:, col] = np.where(agg['long_adj_pos'] >= agg['short_adj_pos'], long_pos[col], short_pos[col])

    agg.loc[:, 'bet'] = np.where(agg['long_adj_pos'] >= agg['short_adj_pos'], 1000, -1000)

    return agg, long_pos, short_pos


def position_one_direction(df, dctv):
    # instrument currency volatility
    df['icv'] = df['close'] * df['stddev']
    # volatility scalar
    df['vs'] = dctv / df['icv']
    # using yesterday's forecast
    df['target_pos'] = df['vs'] * df.shift(1)['forecast'] / 10

    # position
    test = df[['open', 'close', 'forecast', 'target_pos']].copy()
    test = test[1:]
    for i in range(len(test)):
        target_present = test['target_pos'][i]
        if i == 0:
            if target_present <= 0:
                temp = 0
            else:
                temp = round(target_present)
        else:
            target_before = test['adj_pos'][i - 1]
            if target_present <= 0:
                temp = 0
            else:
                if target_before > 0 and 0.9 < target_present / target_before < 1.1:
                    temp = test['adj_pos'][i - 1]
                else:
                    temp = round(target_present)

        test.loc[test.index[i], 'adj_pos'] = temp

    return test


# else (long and short instrument is same)
def position(df, tr_cap, pvt):
    # tr_cap: trade capital, pvt: percentage volatility target
    # annualised cash target volatility
    actv = tr_cap * pvt
    # daily cash target volatility
    dctv = actv / 16

    # instrument currency volatility
    df['icv'] = df['close'] * df['stddev']
    # volatility scalar
    df['vs'] = dctv / df['icv']

    # using yesterday's forecast
    # divide by 10, because its mean is 10
    df['target_pos'] = df['vs'] * df.shift(1)['forecast'] / 10

    # position
    test = df[['close', 'forecast', 'target_pos']].copy()
    # position can be measured after first row (no forecast at first row)
    test = test[1:]

    test.loc[:, 'adj_pos'] = np.where(np.log(np.abs(np.round(test['target_pos'], 0)) /
                                             np.abs(np.round(test.shift(1)['target_pos'].fillna(method='bfill'), 0))) > 0.1
                                      , np.abs(np.round(test['target_pos'], 0))
                                      , np.abs(np.round(test.shift(1)['target_pos'], 0))
                                      )

    return test[1:]
