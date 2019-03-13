import logging
import os
import sys
import time
import datetime as dt
import urllib.request as req
import urllib.parse as pars
import const.stat as ic
import framework.forecast as fc
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

        fh = TimedRotatingFileHandler("C:\SMWJ_LOG\\framework", when="midnight")
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