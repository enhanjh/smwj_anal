import pandas as pd
import query.query_common as qcom
import query.query_rebalance as qreb


# 포트폴리오에 편입된 종목의 종가를 조회함
def retrieve_pf_item_price(sttg_num, sdate, edate):
    param = {
        'sttg_num': sttg_num,
        'sdate': sdate,
        'edate': edate
    }

    return pd.read_sql(qreb.pf_item_price.format(**param), qcom.prd_engine, index_col='tran_day')


print(retrieve_pf_item_price('9', '20180101', '20190101'))