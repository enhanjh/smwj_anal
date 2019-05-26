
pf_item_price = "select a.item" \
                "     , a.tran_day" \
                "     , a.close" \
                "  from price a" \
                " where a.item in (select item " \
                "                    from portfolio " \
                "                   where mode = '{sttg_num}'" \
                "                     and ifnull(del_dt, '99991231') > '{edate}'" \
                "                 )" \
                "   and a.tran_day between '{sdate}' and '{edate}'" \
                "   ;"
