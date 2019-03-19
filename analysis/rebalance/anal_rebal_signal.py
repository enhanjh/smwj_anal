import numpy as np
import const.stat as ic


# 신호 발생기(ewma) (need at least 36 days of data for stddev)
def signal_ewmac(price, fast_win, slow_win, span=35):

    # profit rate
    # anal['return'] = np.log(anal['close']) - np.log(anal['close'].shift(1))
    # anal['stddev'] = anal['return'].ewm(span=span, min_periods=span).std()
    # anal['std_adj'] = anal['stddev'] * anal['close']

    # anal['ewma_fast'] = anal['close'].ewm(span=fast_win, min_periods=fast_win).mean()
    # anal['ewma_slow'] = anal['close'].ewm(span=slow_win, min_periods=slow_win).mean()

    # raw crossover
    # anal['raw_cr'] = anal['ewma_fast'] - anal['ewma_slow']
    # anal['vol_cr'] = anal['raw_cr'] / anal['std_adj']

    # it should have an average absolute value of around 10
    # anal['signal'] = anal['vol_cr'] * scalar

    ewma_fast = price['close'].ewm(span=fast_win, min_periods=fast_win).mean()
    ewma_slow = price['close'].ewm(span=slow_win, min_periods=slow_win).mean()

    raw_crossover = ewma_fast - ewma_slow
    vol_crossover = price['close'].diff().ewm(span=span, min_periods=span).std()

    result = raw_crossover / vol_crossover

    # nan 데이터 제외
    if span > slow_win:
        length = span
    else:
        length = slow_win

    return result[length + 1:]


# 신호 강도 정규화
def signal_scalar(signal):

    avg_abs_fc = signal.abs().rolling(window=slow_win).mean()
    target_fc = ic.TARGET_FC

    return target_fc / avg_abs_fc
