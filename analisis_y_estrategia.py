from ADX import ADX
from RSI import RSI
from ichimoku import ichimoku
from macd import MACD, detectar_div_macd
from multiprocessing import Process
from SeguimientoIchimoku import seguimiento_ichimoku
from BollingerBands import boll_bnd
import time


def analisis_y_estrategia1(ohlc_1min, ohlc_5s, resistencia_punto_mayor1m, resistencia_punto_menor1m,
                           soporte_punto_menor1m,
                           soporte_punto_mayor1m, resistencia_punto_mayor5m, resistencia_punto_menor5m,
                           soporte_punto_menor5m, soporte_punto_mayor5m):
    rsi_28 = RSI(ohlc_5s, 28)
    rsi_14 = RSI(ohlc_5s, 14)
    print(rsi_28.iloc[-1], rsi_14.iloc[-1])
    if (rsi_28.iloc[-1] < 30.0 or rsi_28.iloc[-2] < 30.0) and (
            rsi_14.iloc[-2] < rsi_28.iloc[-2] and rsi_14.iloc[-1] > rsi_28.iloc[-1]) and \
            (ohlc_5s["c"].iloc[-2] < ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if adx_1min.iloc[-1, 0] < 25.0 and (adx_1min.iloc[-1, 1] < 25.0 or
                                            adx_1min.iloc[-1, 1] < adx_1min.iloc[-2, 1]) \
                and (adx_5s.iloc[-1, 1] < adx_5s.iloc[-2, 1]) and (adx_5s.iloc[-1, 2] > adx_5s.iloc[-2, 2]):
            return "comprac"
        else:
            return ""
    elif rsi_28.iloc[-1] > 70.0 and (ohlc_5s["c"].iloc[-2] < ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if (adx_5s.iloc[-1, 0] > 25.0 and adx_5s.iloc[-2, 2] < adx_5s.iloc[-1, 2] > adx_5s.iloc[-1, 1]) and (
                adx_1min.iloc[-2, 2] < adx_1min.iloc[-2, 0] and
                adx_1min.iloc[-1, 2] > adx_1min.iloc[-1, 0]):
            return "compraf"
        else:
            return ""
    elif (rsi_28.iloc[-1] > 70.0 or rsi_28.iloc[-2] > 70.0) and (
            rsi_14.iloc[-2] > rsi_28.iloc[-2] and rsi_14.iloc[-1] < rsi_28.iloc[-1]) and \
            (ohlc_5s["c"].iloc[-2] > ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if adx_1min.iloc[-1, 0] < 25.0 and (adx_1min.iloc[-1, 2] < 25.0 or
                                            adx_1min.iloc[-1, 2] < adx_1min.iloc[-2, 2]) and \
                (adx_5s.iloc[-1, 1] > adx_5s.iloc[-2, 1]) and (adx_5s.iloc[-1, 2] < adx_5s.iloc[-2, 2]):
            return "ventac"
        else:
            return ""
    elif rsi_28.iloc[-1] < 30.0 and (ohlc_5s["c"].iloc[-2] > ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if (adx_5s.iloc[-1, 0] > 25.0 and adx_5s.iloc[-2, 1] < adx_5s.iloc[-1, 1] > adx_5s.iloc[-1, 2]) and (
                adx_1min.iloc[-2, 1] < adx_1min.iloc[-2, 0] and
                adx_1min.iloc[-1, 1] > adx_1min.iloc[-1, 0]):
            return "ventaf"
        else:
            return ""
    else:
        return ""


def analisis_y_estrategia2(ohlc_5s, ohlc_1m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                           sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    ichi_1m = ichimoku(ohlc_1m)
    macd_5s = MACD(ohlc_5s)
    print("compraf", (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
                      ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]))
    print("ventaf", (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
                     ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]))
    if (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
            ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "compraf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min))
        seg.start()
        time.sleep(59)
        return ""
    elif (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
          ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "ventaf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min))
        seg.start()
        time.sleep(59)
        return ""
    if (res_max_1min > ohlc_5s['c'].iloc[-1] > res_min_1min or res_max_5min > ohlc_5s['c'].iloc[-1] > res_min_5min) \
            and detectar_div_macd(macd_5s, ohlc_5s, "bajista"):
        return "ventac"
    elif (sop_min_1min < ohlc_5s['c'].iloc[-1] < sop_max_1min or sop_min_5min < ohlc_5s['c'].iloc[-1] < sop_max_5min) \
            and detectar_div_macd(macd_5s, ohlc_5s, "alcista"):
        return "comprac"
    else:
        return ""


def analisis_y_estrategia3(ohlc_5s, ohlc_1m, ohlc_5m, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                           sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    ichi_1m = ichimoku(ohlc_1m)
    ichi_5s = ichimoku(ohlc_5s)
    print(ichi_1m["Senkou span A"].iloc[-26], ohlc_5s['c'].iloc[-1], ichi_1m["Senkou span B"].iloc[-26])
    if (ichi_1m["Senkou span A"].iloc[-26] < ohlc_5s['c'].iloc[-1] < ichi_1m["Senkou span B"].iloc[-26]) or \
            (ichi_1m["Senkou span B"].iloc[-26] < ohlc_5s['c'].iloc[-1] < ichi_1m["Senkou span A"].iloc[-26]):
        bollinger_1m = boll_bnd(ohlc_1m)
        adx_5s = ADX(ohlc_5s, 14)
        rsi_5s = RSI(ohlc_5s, periodo=7)
        print(bollinger_1m["BB_up"].iloc[-1])
        if (ohlc_5s['c'] > bollinger_1m["BB_up"].iloc[-1]) and (adx_5s["ADX"].iloc[-1] < 32.0) and (
                rsi_5s.iloc[-1] < 70):
            return "ventac"
        elif (ohlc_5s['c'] < bollinger_1m["BB_dn"].iloc[-1]) and (adx_5s["ADX"].iloc[-1] < 32.0) and (
                rsi_5s.iloc[-1] > 30):
            return "comprac"
        else:
            return ""
    if (res_max_1min >= res_min_1min > ohlc_5s['c'].iloc[-1]) and (res_max_5min >= res_min_5min > ohlc_5s['c'].iloc[-1])\
             and (ohlc_5s['c'].iloc[-1] > ichi_5s['Senkou span A'].iloc[-26] >= ichi_5s['Senkou span B'].iloc[-26] or
     ichi_5s['Senkou span A'].iloc[-26] <= ichi_5s['Senkou span B'].iloc[-26] < ohlc_5s['c'].iloc[-1]):
        adx_5s = ADX(ohlc_5s, periodos=50)
        rsi_5s = RSI(ohlc_5s, periodo=2)
        if (adx_5s["ADX"].iloc[-1] > 15.0 and adx_5s["DI+"].iloc[-1] > adx_5s["DI-"].iloc[-1]) and \
                (adx_5s["ADX"].iloc[-2] < adx_5s["ADX"].iloc[-1]):
            if rsi_5s.iloc[-2] < 30.0 and ohlc_5s['c'].iloc[-2] < ohlc_5s['c'].iloc[-1]:
                return "compraf"
            else:
                return ""
    if (sop_min_1min <= sop_max_1min < ohlc_5s['c'].iloc[-1]) and (sop_min_5min <= sop_max_5min < ohlc_5s['c'].iloc[-1])\
            and (ohlc_5s['c'].iloc[-1] < ichi_5s['Senkou span A'].iloc[-26] <= ichi_5s['Senkou span B'].iloc[-26] or
                 ichi_5s['Senkou span A'].iloc[-26] >= ichi_5s['Senkou span B'].iloc[-26] > ohlc_5s['c'].iloc[-1]):
        adx_5s = ADX(ohlc_5s, periodos=50)
        rsi_5s = RSI(ohlc_5s, periodo=2)
        if (adx_5s["ADX"].iloc[-1] > 15.0 and adx_5s["DI+"].iloc[-1] < adx_5s["DI-"].iloc[-1]) and \
                (adx_5s["ADX"].iloc[-2] < adx_5s["ADX"].iloc[-1]):
            if rsi_5s.iloc[-2] > 70.0 and ohlc_5s['c'].iloc[-2] > ohlc_5s['c'].iloc[-1]:
                return "ventaf"
            else:
                return ""
        else:
            return ""
