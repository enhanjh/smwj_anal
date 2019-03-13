
item_price = "select a.item" \
             "     , a.tran_day" \
             "     , a.open" \
             "     , a.close" \
             "  from price a" \
             " where a.item = '{item}'" \
             "   and a.tran_day between '{sdate}' and '{edate}';"
