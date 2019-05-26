import numpy as np
import const.stat as ic


# 신호 발생기(ewma) (변동성 계산을 위해 최소 35 일의 데이터 필요)
def signal_ewmac(price, fast_win, slow_win, span=35):

    price_grp = price.groupby('item')

    ewma_fast = price_grp.apply(lambda x: x['close'].ewm(span=fast_win, min_periods=fast_win).mean())
    ewma_slow = price_grp.apply(lambda x: x['close'].ewm(span=slow_win, min_periods=slow_win).mean())

    raw_crossover = ewma_fast - ewma_slow
    volatility = price_grp.apply(lambda x: x['close'].diff().ewm(span=span, min_periods=span).std())

    # 빠른 추세와 느린 추세의 차이와 일간 변동성의 배수
    # 예. 평상시의 변동성보다 추세가 급격히 변하고 있다.
    raw_signal = raw_crossover.T / volatility.T  # vol_crossover

    # nan 데이터 제외
    if span > slow_win:
        length = span
    else:
        length = slow_win

    return raw_signal[length + 1:], volatility.T[length + 1:]


'''
예시
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

raw_signal, volatility = signal_ewmac(prices, 16, 64)
prices.groupby('item').describe()
raw_signal.describe()
raw_signal.tail()
raw_signal.plot()
'''


# 신호 강도 정규화
def signal_scaling(signal, fast_win=25):

    # 신호의 최고치를 20 으로 함
    capped_signal = signal.copy()
    capped_signal[capped_signal > 20] = 20

    # 변동성의 추세가 최근 5 주 정도 지속된다고 가정함
    avg_abs_signal = capped_signal.abs().ewm(span=fast_win, min_periods=fast_win).mean()
    static_target_signal = ic.TARGET_SIGNAL

    return capped_signal[fast_win+1:] * (static_target_signal / avg_abs_signal[fast_win+1:])


'''
예시

scaled_signal = signal_scaling(raw_signal, 64)
scaled_signal.describe()
scaled_signal.tail()
scaled_signal.plot()
'''


# 신호 상관관계 확인


# 한 상품이 여러개 신호를 가지고 있는지를 어떻게 알지? 내가 알지(데이터프레임 조인)
# TODO : 향후 자동화에 대한 고려 필요
# 신호 조합 :
def signal_combiner():

    return 'asdf'

