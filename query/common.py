import const.stat as ic
from sqlalchemy import create_engine


prd_scott = ic.prd_config["user"]
prd_tiger = ic.prd_config["password"]
prd_host = ic.prd_config["host"]
# dev_scott = ic.prd_config["user"]
# dev_tiger = ic.prd_config["password"]
# dev_host = ic.prd_config["host"]

prd_bind = 'mysql+mysqlconnector://' + prd_scott + ':' + prd_tiger + '@' + prd_host + ':3306/smwj'
# dev_bind = 'mysql+mysqlconnector://' + dev_scott + ':' + dev_tiger + '@' + dev_host + ':3306/smwj'
prd_engine = create_engine(prd_bind)
# dev_engine = create_engine(dev_bind)


item_price = "select a.item" \
             "     , a.tran_day" \
             "     , a.open" \
             "     , a.close" \
             "  from price a" \
             " where a.item = '{item}'" \
             "   and a.tran_day between '{sdate}' and '{edate}';"
