import pandas as pd
import numpy as np
import query.query_common as qcom
import query.query_trend as qreb


# 포트폴리오에 편입된 종목의 종가를 조회함
def retrieve_pf_item_price(sttg_num, sdate, edate):
    param = {
        'sttg_num': sttg_num,
        'sdate': sdate,
        'edate': edate
    }

    return pd.read_sql(qreb.pf_item_price.format(**param), qcom.prd_engine, index_col='tran_day')


'''
예시

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

prices = retrieve_pf_item_price('9', '20180101', '20190101')
prices.groupby('item').describe()
'''


def dynamic_returns(price, position):

    # 수익률 계산 방식 : ln(당일 증권평가금액) - ln(당일 현금변동누적)
    # 현금 : 증권을 매도할 경우 늘어나고, 증권을 매수할 경우 줄어듦
    # 증권 : 매일 종가로 공정가치 평가
    security_bal = price * position
    cash_tr = price * position.diff()
    cash_tr = cash_tr.fillna(value=0, limit=1)  # 첫 번째 행 0 으로 채우기

    # 연속된 기간만의 현금누적금액을 구하기 위한 flag
    # 다음 거래에 지난 거래의 손익이 누적되지 않게함
    position_flag = position == 0  # 포지션이 0 이고,
    cash_flag = abs(cash_tr) > 0  # 현금이 0 보다 클 경우가 한 거래 사이클의 종결 시점
    end_flag = position_flag & cash_flag

    cash_bal = cash_tr.cumsum()
    cyclical_cash_bal = cash_bal * end_flag
    cyclical_cash_bal = cyclical_cash_bal.replace({-0: np.NaN, 0: np.NaN})
    cyclical_cash_bal = cyclical_cash_bal.shift(1).fillna(method='ffill').fillna(0)
    cash_bal = cash_bal - cyclical_cash_bal

    # 누적 수익률에서 직전 누적 수익률을 차감할 경우, 최근 시점의 수익률이 계산됨
    cum_returns = np.log(security_bal) - np.log(cash_bal)
    returns = cum_returns.diff().fillna(value=0, limit=1)
    returns = returns.replace([np.inf, -np.inf, np.NaN], 0)

    corr = returns.corr()

    return returns, corr
