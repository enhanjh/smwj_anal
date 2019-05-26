import logging
import os
import sys
import time
import datetime as dt
import urllib.request as req
import urllib.parse as pars
import interface.bot as bot
import xml.etree.ElementTree as et
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Operator:
    def __init__(self):
        # variable init
        self.bot_smwj = object()
        self.logger = object()
        self.db_session = object()
        self.logger = object()
        self.bind = str()
        self.today = time.strftime("%Y%m%d")

        # sub classes init
        self.logger_start()
        self.chatbot_start()
        self.orm_init()

        # business day check
        if len(sys.argv) > 1 and sys.argv[1] == 'server':
            if self.bizday_check():
                # etl run
                if len(sys.argv) > 2 and sys.argv[2] is not None:
                    self.etl_run(sys.argv[2])
                else:
                    self.etl_run(self.today)
            else:
                self.shut_down()

    def chatbot_start(self):
        self.bot_smwj = bot.BotSmwj(self)
        self.bot_smwj.start()
        self.bot_smwj.send_message("smwj-fw is starting up")

    def logger_start(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        formatter = logging.Formatter('[%(levelname)s:%(lineno)s] %(asctime)s > %(message)s')
        self.logger = logging.getLogger()

        fh = TimedRotatingFileHandler("C:\SMWJ_LOG\\analysis", when="midnight")
        fh.setFormatter(formatter)
        fh.suffix = "_%Y%m%d.log"

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)

    def orm_init(self):
        scott = ic.dbconfig["user"]
        tiger = ic.dbconfig["password"]
        host  = ic.dbconfig["host"]
        self.bind = 'mysql+mysqlconnector://' + scott + ':' + tiger + '@' + host + ':3306/smwj'

        engine = create_engine(self.bind)
        dbsession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db_session = dbsession()

    def fw_run(self, edate):
        # 0. 마스터 db 에 데이터 입력 : 향후 개발
        # 1. 마스터 db 에서 종가 확인 대상 종목 조회
        #   1) 신규 종목 추가됐을 경우 : 향후 개발
        #   2) 기존 종목 제외됐을 경우 : 향후 개발
        # 2. 종목들의 종가 확인
        # 3. forecast 계산
        # 4. position 계산
        # 5. 2~4 반복
        # 6. 종합 position 계산
        #   * 계산한 포지션과 현재 포지션에 차이가 10% 이내일 경우 포지션 변동 없음
        #   * 신규 종목 추가,제외시 포지션 리밸런싱 : 향후 개발
        # 7. 결과값 db 저장
        df_forecast = fc.forecast_ewmac()
        eb.login(self.logger)
        eb.retrieve_item_mst(self.logger, self.bind)

        #edate = self.today
        row_cnt = "1"

        d = datetime.today() - timedelta(days=10)
        sdate = d.strftime("%Y%m%d")

        eb.retrieve_daily_chart(self.logger, self.bind, self.db_session, edate, edate)
        eb.retrieve_investor_volume(self.logger, self.bind, edate, edate)
        eb.retrieve_market_index_tr_amt(self.logger, self.bind, edate, edate)
        eb.retrieve_abroad_index(self.logger, self.bind, edate, row_cnt)
        eb.retrieve_market_liquidity(self.logger, self.bind, edate, sdate, row_cnt)

        self.shut_down()

    def bizday_check(self):
        url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo'
        query_params = '?' + pars.urlencode(
            {pars.quote_plus('serviceKey'): ic.publicdata['key'], pars.quote_plus('solYear'): self.today[:4],
             pars.quote_plus('solMonth'): self.today[4:6]})

        request = req.Request(url + query_params)
        request.get_method = lambda: 'GET'
        response_body = req.urlopen(request).read()

        root = et.fromstring(response_body)
        holidays = list()
        for locdate in root.iter('locdate'):
            holidays.append(locdate.text)

        self.logger.info("holiday list")
        self.logger.info(holidays)

        bizday = True
        if dt.datetime.today().weekday() >= 5:
            bizday = False
            self.bot_smwj.send_message("today is weekend")
        elif self.today in holidays:
            bizday = False
            self.bot_smwj.send_message("today is holiday")
        elif self.today[4:8] == '0501':
            bizday = False
            self.bot_smwj.send_message("today is mayday")

        return bizday

    def shut_down(self):
        self.bot_smwj.send_message("smwj-fw is shutting down")

        os._exit(0)


if __name__ == "__main__":
    op = Operator()

    import const.stat as ic
    import pandas as pd
    import numpy as np
    # import matplotlib.pyplot as plt
    import analysis.trend.anal_trend_common as com
    import analysis.trend.anal_trend_signal as sig
    import analysis.trend.anal_trend_position as pos

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    '''가격 조회'''
    # prices = com.retrieve_pf_item_price('9', '20180101', '20190101')
    prices = com.retrieve_pf_item_price('10', '20110801', '20161231')
    # prices.groupby('item').describe()
    # prices.head(5)

    '''신호 및 변동성 계산'''
    # raw_signal, volatility = sig.signal_ewmac(prices, 16, 64)
    raw_signal_s, volatility_s = sig.signal_ewmac(prices, 4, 16)
    raw_signal_m, volatility_m = sig.signal_ewmac(prices, 16, 64)
    raw_signal_l, volatility_l = sig.signal_ewmac(prices, 64, 256)

    raw_signal = raw_signal_s.join(raw_signal_m, how='inner', rsuffix='_m')
    raw_signal = raw_signal.join(raw_signal_l, how='inner', rsuffix='_l')
    # raw_signal.head(5)
    # raw_signal.describe()
    # raw_signal.tail()

    test_df = raw_signal_s[['122630']]
    test_df = test_df.join(prices.groupby('item').apply(lambda x: x['close']).T[['122630']], how='inner', rsuffix='_prc')

    ax1 = test_df[['122630']].plot()

    ax2 = ax1.twinx()
    ax2.spines['right'].set_position(('axes', 1.0))
    test_df[['122630_prc']].plot(ax=ax2, color='Green')

    test_df.plot()
    # plt.legend(raw_signal_s.columns)
    # plt.subplot(211)
    # plt.plot(raw_signal_s)
    # plt.subplot(212)
    # plt.plot(prices.pivot(columns='item').pct_change())

    '''신호 스케일링'''
    scaled_signal = sig.signal_scaling(raw_signal, 25)
    # scaled_signal.abs().describe()
    # scaled_signal.tail()

    '''스케일링한 신호 비교'''
    # test_ewm_fast = raw_signal * 10 / raw_signal.abs().ewm(span=32).mean()
    # test_ewm_fast1 = raw_signal * 10 / raw_signal.abs().ewm(span=32, min_periods=32).mean()
    # test_ewm_slow = raw_signal * 10 / raw_signal.abs().ewm(span=64).mean()
    # test_mean = raw_signal * 10 / raw_signal.abs().rolling(window=64).mean()
    # test_static = raw_signal * 3.75

    # test_ewm_fast.abs().describe()
    # test_ewm_fast1.abs().describe()
    # test_ewm_slow.abs().describe()
    # test_mean.abs().describe()
    # test_static.abs().describe()

    # scaled_signal
    # plt.subplot(212)
    # plt.plot(scaled_signal)

    # scaled_signal.describe()
    # scaled_signal.tail()
    # volatility.describe()
    # volatility.tail()

    '''포지션 계산'''
    raw_pos = pos.position_sizing(scaled_signal, volatility, 10000000, 0.25)
    # raw_pos.describe()

    '''포지션 조정'''
    adj_pos = pos.position_stabilizing(raw_pos)

    # adj_pos.describe()
    # adj_pos.head(20)
    # raw_pos.head(20)

    adj_prc = prices.groupby('item').apply(lambda x: x['close']).T
    adj_prc = adj_prc[adj_pos.index[0]:]

    '''포지션 금액 확인'''
    returns, corr = com.dynamic_returns(adj_prc, adj_pos)

    # corr
    # adj_prc.describe()

    # adj_pos.head(20)
    # security_val.head(20)
    # cash_val.head(20)
    # account_val.head(20)
    # returns.head(20)
    # returns.sum()
    # np.mean(np.exp(returns) - 1)

    # need 'openpyxl' package
    with pd.ExcelWriter('v2_test_v1.1_20190424.xlsx') as writer:
        adj_prc.to_excel(writer, sheet_name='price')
        adj_pos.to_excel(writer, sheet_name='position')
        returns.to_excel(writer, sheet_name='returns')
