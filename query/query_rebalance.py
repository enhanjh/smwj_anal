
pf_item_price = "select a.item" \
             "     , a.tran_day" \
             "     , a.open" \
             "     , a.close" \
             "  from price a" \
             " where a.item in (select item from portfolio where mode = '{sttg_num}')" \
             "   and a.tran_day between '{sdate}' and '{edate}';"
