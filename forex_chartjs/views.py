from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
import psycopg2
from .serializers import *
from .models import *
from rest_framework import viewsets
import requests
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json



bid_data_fetch = []

def get_data_mt5(currency_name):
    try:
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            return None
        else:
            ask = mt5.symbol_info_tick(currency_name).ask
            bid = mt5.symbol_info_tick(currency_name).bid
            ask = round(ask, 5)
            bid = round(bid, 5)

            current_price = (ask + bid) / 2
            current_price = round(current_price, 5)

            return current_price, ask, bid
    except Exception as e:
        print("[ERROR]", e)
        return None


def get_data(request):
    mydb = psycopg2.connect(
        # database="forex_db", user='postgres', password='admin', host='127.0.0.1', port='5432')
        database="postgres", user='postgres', password='admin', host='127.0.0.1', port='5432')

    currency__ = ""
    interval__ = ""
    method_ = "1"

    if request.GET.get('currency'):
        currency__ = request.GET.get('currency')

    if request.GET.get('interval'):
        interval__ = request.GET.get('interval')
        interval__ = interval__ + "_min"

    if request.GET.get('method_'):
        method_ = request.GET.get('method_')

    currency = "AUDUSD"
    time_interval = "15Min"
    mydb.autocommit = True
    cursor = mydb.cursor()

    # if currency__ == '':
    #     sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency + "' "
    #     # sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency + "' "
    # else:
    #     sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_current_price)
    # result_current_price = cursor.fetchall()[0][0]

    # if currency__ == '':
    #     sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency + "' "
    # else:
    #     sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_query_buy)
    # result_buy = cursor.fetchall()[0][0]

    # if currency__ == '':
    #     sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency + "' "
    # else:
    #     sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_query_sell)
    # result_sell = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_predicted_high_low = "Select currency, time_interval, high, high_prediction," \
                                       " TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, " \
                                       "low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low " \
                                       "FROM predicted_high_low_vw where currency = '" + currency + "'"
    else:
        sql_query_predicted_high_low = "Select currency, time_interval, high, high_prediction, TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency__ + "'"

    cursor.execute(sql_query_predicted_high_low)
    result_high_low = cursor.fetchall()

    if currency__ != '' and interval__ == '':
        sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' order by current_time_ asc"
    elif currency__ != '' and interval__ != '':
        sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' and time_interval = '" + interval__ + "'order by current_time_ asc"
    else:
        sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data order by current_time_ asc"

    cursor.execute(sql_query_historical_data)
    result_historical = cursor.fetchall()

    currency_ = Currency.objects.all()
    time_interval = Interval.objects.all()

    context = {
        # "Buy": result_buy,
        # "Sell": result_sell,
        "high_low": result_high_low,
        "historical_data": result_historical,
        "Get_currency": currency_,
        "Get_interval": time_interval,
        "currency": currency__,
        # "current_price": result_current_price,
    }

    # return render(request, 'chartjs/demo_v2.html', context)
    return render(request, 'chartjs/demo_v2.html', context)
    # return render(request, 'chartjs/demo_v1.html', context)


def get_currency(request):
    mydb = psycopg2.connect(
        # database="postgres", user='postgres', password='admin', host='127.0.0.1', port='5432')
        database="forex_db", user='postgres', password='admin', host='192.168.1.198', port='5432')

    mydb.autocommit = True
    cursor = mydb.cursor()

    currency = "GBPUSD"
    currency__ = ""
    interval__ = ""

    if request.GET.get('currency'):
        currency__ = request.GET.get('currency')

    if request.GET.get('interval'):
        interval__ = request.GET.get('interval')
        interval__ = interval__ + "_min"

    if currency__ == '':
        current_price, ask_price, bid_price = get_data_mt5(currency__)
        # sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency + "' "
    else:
        current_price, ask_price, bid_price = get_data_mt5(currency__)
        # sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_current_price)
    # result_current_price = cursor.fetchall()[0][0]
    # cursor = None
    # cursor = mydb.cursor()

    # if currency__ == '':
    #     sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency + "' "
    # else:
    #     sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_query_buy)
    # result_buy = cursor.fetchall()[0][0]

    # if currency__ == '':
    #     sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency + "' "
    # else:
    #     sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency__ + "' "
    # cursor.execute(sql_query_sell)
    # result_sell = cursor.fetchall()[0][0]

    if currency__ == '':
        # sql_query_high_low = "Select currency, time_interval, high, high_prediction, TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low FROM predicted_high_low_vw
        # where currency = '" + currency + "' order by time_interval_id asc"
        sql_query_bid_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_bid_tbl"
        sql_query_ask_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_ask_tbl"
    else:

        # sql_query_high_low = "Select currency, time_interval, high, high_prediction, TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency__ + "' order by time_interval_id asc "
        sql_query_bid_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_bid_tbl"
        sql_query_ask_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_ask_tbl"
    cursor.execute(sql_query_bid_tbl)
    result_bid_tbl = cursor.fetchall()
    cursor.execute(sql_query_ask_tbl)
    result_ask_tbl = cursor.fetchall()

    # if currency__ == '':
    #     # sql_query_high_low = "Select currency, time_interval, high, high_prediction, TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low FROM predicted_high_low_vw
    #     # where currency = '" + currency + "' order by time_interval_id asc"
    #     sql_query_ask_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_ask_tbl"
    # else:
    #
    #     # sql_query_high_low = "Select currency, time_interval, high, high_prediction, TO_CHAR(date_time_hit_high, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_high, low, low_prediction, TO_CHAR(date_time_hit_low, 'DD/MM/YYYY HH:MM:SS') as date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency__ + "' order by time_interval_id asc "
    #     sql_query_ask_tbl = "SELECT minutes_1 , minutes_5 , minutes_15 , minutes_30 , minutes_60, minutes_240 FROM forex_pred_ask_tbl"
    # cursor.execute(sql_query_ask_tbl)
    # # result_high_low = cursor.fetchall()
    # result_ask_tbl = cursor.fetchall()


    if currency__ != '' and interval__ == '':
        # sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' order by current_time_ asc"
        sql_query_historical_data_bid = "SELECT interval, actual_bid, actual_max_bid, buy_prediction, actual_high_dt, prediction_dt FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' limit 5;"

        get_bid_predcition = "Select buy_prediction FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"

        sql_query_historical_data_ask = " SELECT interval, actual_ask, actual_min_ask, sell_prediction, actual_low_dt, prediction_dt FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"'  LIMIT 5;"
        # cursor.execute(sql_query_historical_data_ask)
        # result_historical_ask = cursor.fetchall()

    # elif currency__ != '' and interval__ != '':
    #     sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' and time_interval = '" + interval__ + "' order by current_time_ asc"
    else:
        # sql_query_historical_data_bid = "SELECT interval, actual_bid, actual_max_bid, buy_prediction, TO_CHAR(actual_high_dt, 'DD/MM/YYYY HH:MM:SS') as actual_high_dt, " \
        #                                 "TO_CHAR(prediction_dt, 'DD/MM/YYYY HH:MM:SS') as prediction_dt FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' and currency = '"+currency__+"' ORDER BY prediction_dt DESC LIMIT 5;"

        sql_query_historical_data_bid = "SELECT interval, current_dt, actual_bid, actual_min_max_bid, buy_prediction, prediction_dt, actual_low_high_dt FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 5;"
        get_bid_predcition = "Select buy_prediction FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"
        sql_query_historical_data_ask = "SELECT interval, current_dt, actual_ask, actual_min_ask, sell_prediction, prediction_dt, actual_low_dt FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 5;"

        # sql_query_historical_data_ask = " SELECT interval, actual_ask, actual_min_ask, sell_prediction, TO_CHAR(actual_low_dt, 'DD/MM/YYYY HH:MM:SS') as actual_low_dt, " \
        #                                 "TO_CHAR(prediction_dt, 'DD/MM/YYYY HH:MM:SS') as prediction_dt FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 5 ;"

    cursor.execute(sql_query_historical_data_ask)
    result_historical_ask = cursor.fetchall()

    cursor.execute(get_bid_predcition)
    bid_prediction_value = cursor.fetchall()[0][0]
    print("bid_prediction_value",bid_prediction_value)

    cursor.execute(sql_query_historical_data_bid)
    result_historical_bid = cursor.fetchall()
    # print(result_historical_bid)


    # # if currency__ != '' and interval__ == '':
    #     # sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' order by current_time_ asc"
    #     sql_query_historical_data_ask = " SELECT interval, actual_ask, actual_min_ask, sell_prediction, actual_low_dt, prediction_dt FROM forex_pred_ask_logs_tbl LIMIT 5;"
    #     print("sql_query_historical_data_ask", sql_query_historical_data_ask)
    # # elif currency__ != '' and interval__ != '':
    # #     sql_query_historical_data = "SELECT TO_CHAR(current_time_, 'DD/MM/YYYY HH:MM:SS') as current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, TO_CHAR(target_datetime, 'DD/MM/YYYY HH:MM:SS') as target_datetime, TO_CHAR(datetime_hit_high, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_high, TO_CHAR(datetime_hit_low, 'DD/MM/YYYY HH:MM:SS') as datetime_hit_low from historical_data where currency = '" + currency__ + "' and time_interval = '" + interval__ + "' order by current_time_ asc"
    # else:
    #     sql_query_historical_data_ask = " SELECT interval, actual_ask, actual_min_ask, sell_prediction, actual_low_dt, prediction_dt FROM forex_pred_ask_logs_tbl LIMIT 5;"
    #
    # cursor.execute(sql_query_historical_data_ask)
    # result_historical_ask = cursor.fetchall()

    first_bid_arrow = "SELECT check_buy FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"
    second_bid_arrow = "SELECT check_strong_buy FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"
    third_bid_arrow = "SELECT check_bullish_buy FROM forex_pred_bid_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"

    # first_ask_arrow = "SELECT check_sell FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"
    # second_ask_arrow = "SELECT check_strong_sell FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"
    # third_ask_arrow = "SELECT check_bullish_sell FROM forex_pred_ask_logs_tbl where interval = '"+interval__+"' ORDER BY prediction_dt DESC LIMIT 1;"

    # cursor.execute(first_bid_arrow)
    # first_bid_arrow_ = cursor.fetchall()[0][0]
    # # print(first_bid_arrow_)
    #
    # cursor.execute(second_bid_arrow)
    # second_bid_arrow_ = cursor.fetchall()[0][0]
    # # print(second_bid_arrow_)
    #
    # cursor.execute(third_bid_arrow)
    # third_bid_arrow_ = cursor.fetchall()[0][0]
    # print(third_bid_arrow_)

    # cursor.execute(first_ask_arrow)
    # first_ask_arrow_ = cursor.fetchall()[0][0]
    # # print(first_ask_arrow_)
    #
    # cursor.execute(second_ask_arrow)
    # second_ask_arrow_ = cursor.fetchall()[0][0]
    # # print(second_ask_arrow_)
    # cursor.execute(third_ask_arrow)
    # third_ask_arrow_ = cursor.fetchall()[0][0]
    # # print(third_ask_arrow_)

    # first_bid_arrow__ = "Buy"
    # second_bid_arrow__ = "Strong Buy"
    # # third_bid_arrow__ = "Bullish Buy"
    # first_ask_arrow__ = "Sell"
    # second_ask_arrow__ = "Strong Sell"
    # # third_ask_arrow__ = "Bullish Sell"
    response = {
    # 'method' : method_,
    # 'current_price': current_price,
    # 'result_buy': str(result_buy),
    # 'result_sell': str(result_sell),
    # 'result_high_low': result_high_low,
    'result_bid_tbl': result_bid_tbl,
    'result_ask_tbl': result_ask_tbl,
    'result_historical': result_historical_bid,
    'result_historical_ask': result_historical_ask,
    'ask_price': ask_price,
    'bid_price': bid_price,
    'bid_prediction_value':bid_prediction_value,
    # 'first_bid_arrow_':first_bid_arrow_,
    # 'second_bid_arrow_':second_bid_arrow_,
    # 'third_bid_arrow_':third_bid_arrow_
    # 'first_ask_arrow_': first_ask_arrow_,
    # 'second_ask_arrow_': second_ask_arrow_,
    # 'third_ask_arrow_': third_ask_arrow_
    }

    return JsonResponse(response)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class IntervalViewSet(viewsets.ModelViewSet):
    queryset = Interval.objects.all()
    serializer_class = IntervalSerializer
