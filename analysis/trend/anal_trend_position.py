import numpy as np
import pandas as pd


# 포지션 결정
def position_sizing(signal, volatility, tr_cap, pvt):
    # tr_cap: trade capital
    # pvt: percentage volatility target
    # actv: annualised cash target volatility
    # dctv: daily cash target volatility
    actv = tr_cap * pvt
    dctv = actv / 16

    len_signal = len(signal.index)
    len_vol = len(volatility.index)
    len_pos = min(len_signal, len_vol)

    # instrument currency volatility
    # TODO : 선물 등 거래단위가 1 개가 아닐 경우 추가 개발 필요
    icv = volatility

    vol_scalar = dctv / icv
    raw_position = vol_scalar.tail(len_pos) * signal.tail(len_pos) / 10

    # short 거래는 없음
    raw_position[raw_position < 0] = 0

    return raw_position


'''
예시
scaled_signal.describe()
scaled_signal.tail()
volatility.describe()
volatility.tail()

raw_pos = position_sizing(scaled_signal, volatility, 10000000, 0.25)
raw_pos.describe()
'''

_pos_ = None


def position_comparison(pos_row):
    global _pos_
    test = abs((pos_row - _pos_) / _pos_) > 0.1
    _pos_ = pos_row * test + _pos_ * ~test
    return _pos_


# 포지션 조정(거래가 너무 자주 일어나지 않도록)
def position_stabilizing(position):
    global _pos_
    _pos_ = position.iloc[0]
    adj_pos = position.copy()
    adj_pos[1:] = position[1:].apply(lambda x: position_comparison(x), axis=1)

    return adj_pos


'''
예시
raw_pos.describe()
raw_pos.tail()

adj_pos = position_stabilizing(raw_pos)
adj_pos.head(20)
raw_pos.head(20)
'''

