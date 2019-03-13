import numpy as np


# ewma forecast (need at least 36 days of data for stddev)
def forecast_ewmac(anal, fast_win, slow_win, scalar, span):

    # profit rate
    anal['return'] = np.log(anal['close']) - np.log(anal['close'].shift(1))
    anal['stddev'] = anal['return'].ewm(span=span, min_periods=span).std()
    anal['std_adj'] = anal['stddev'] * anal['close']

    anal['ewma_fast'] = anal['close'].ewm(span=fast_win, min_periods=fast_win).mean()
    anal['ewma_slow'] = anal['close'].ewm(span=slow_win, min_periods=slow_win).mean()

    # raw crossover
    anal['raw_cr'] = anal['ewma_fast'] - anal['ewma_slow']
    anal['vol_cr'] = anal['raw_cr'] / anal['std_adj']

    # it should have an average absolute value of around 10
    anal['forecast'] = anal['vol_cr'] * scalar

    if span > slow_win:
        leng = span
    else:
        leng = slow_win

    return anal[leng + 1:]
