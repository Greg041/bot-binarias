from ADX import ADX
from RSI import RSI
from ichimoku import ichimoku
from macd import MACD, detectar_div_macd, detectar_div_historigrama
from multiprocessing import Process
from SeguimientoIchimoku import seguimiento_ichimoku
from BollingerBands import boll_bnd
from SeguimientoDivergencia import seguimiento_div
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


def analisis_y_estrategia2(ohlc_5s, ohlc_1m, ohlc_5m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                           sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    ichi_1m = ichimoku(ohlc_1m)
    macd_5s = MACD(ohlc_5s)
    adx_1m = ADX(ohlc_1m)
    print("compraf", (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
                      ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]))
    print("ventaf", (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
                     ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]))
    if (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
            ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "compraf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                         sop_min_1min, sop_max_1min))
        seg.start()
        time.sleep(120)
        return ""
    elif (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
          ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "ventaf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                         sop_min_1min, sop_max_1min))
        seg.start()
        time.sleep(120)
        return ""
    if adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI+"].iloc[-1] > adx_1m["DI-"].iloc[-1]:
        print("en res 1 min", res_max_1min > ohlc_5s['c'].iloc[-1] > res_min_1min)
        print("en res 5 min", res_max_5min > ohlc_5s['c'].iloc[-1] > res_min_5min)
        if (res_max_1min > ohlc_5s['c'].iloc[-1] > res_min_1min or res_max_5min > ohlc_5s['c'].iloc[-1] > res_min_5min) \
                and detectar_div_macd(macd_5s, ohlc_5s, "bajista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_5s, par, "bajista", macd_5s["MACD"].iloc[-2]))
            seg.start()
            return ""
        else:
            return ""
    elif adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI-"].iloc[-1] > adx_1m["DI+"].iloc[-1]:
        print("en sop 1 min", sop_min_1min < ohlc_5s['c'].iloc[-1] < sop_max_1min)
        print("en sop 5 min", sop_min_5min < ohlc_5s['c'].iloc[-1] < sop_max_5min)
        if (sop_min_1min < ohlc_5s['c'].iloc[-1] < sop_max_1min or sop_min_5min < ohlc_5s['c'].iloc[-1] < sop_max_5min) \
                and detectar_div_macd(macd_5s, ohlc_5s, "alcista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_5s, par, "alcista", macd_5s["MACD"].iloc[-2]))
            seg.start()
            return ""
        else:
            return ""
    else:
        return ""


def analisis_y_estrategia_2_2(ohlc_1m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                              sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    ichi_1m = ichimoku(ohlc_1m)
    print("compraf", (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
                      ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]))
    print("ventaf", (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
                     ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]))
    if (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span B"].iloc[-2] and
            ichi_1m["Senkou span A"].iloc[-1] > ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "compraf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                         sop_min_1min, sop_max_1min))
        seg.start()
        time.sleep(120)
        return ""
    elif (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span B"].iloc[-2] and
          ichi_1m["Senkou span A"].iloc[-1] < ichi_1m["Senkou span B"].iloc[-1]):
        seg = Process(target=seguimiento_ichimoku, args=(ohlc_1m, ichi_1m, par, "ventaf", res_max_5min, res_min_5min,
                                                         sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                         sop_min_1min, sop_max_1min))
        seg.start()
        time.sleep(120)
        return ""
    else:
        return ""


def analisis_y_estrategia_2_3(ohlc_5s, ohlc_1m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                              sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    macd_5s = MACD(ohlc_5s)
    adx_1m = ADX(ohlc_1m)
    print("en res 1 min", res_max_1min > ohlc_5s['c'].iloc[-1] > res_min_1min)
    print("en res 5 min", res_max_5min > ohlc_5s['c'].iloc[-1] > res_min_5min)
    if adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI+"].iloc[-1] > adx_1m["DI-"].iloc[-1]:
        if (res_max_1min > ohlc_5s['c'].iloc[-1] > res_min_1min or res_max_5min > ohlc_5s['c'].iloc[-1] > res_min_5min)\
                and detectar_div_macd(macd_5s, ohlc_5s, "bajista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_5s, par, "bajista", macd_5s["MACD"].iloc[-2]))
            seg.start()
            return ""
        else:
            return ""
    elif adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI-"].iloc[-1] > adx_1m["DI+"].iloc[-1]:
        print("en sop 1 min", sop_min_1min < ohlc_5s['c'].iloc[-1] < sop_max_1min)
        print("en sop 5 min", sop_min_5min < ohlc_5s['c'].iloc[-1] < sop_max_5min)
        if (sop_min_1min < ohlc_5s['c'].iloc[-1] < sop_max_1min or sop_min_5min < ohlc_5s['c'].iloc[-1] < sop_max_5min) \
                and detectar_div_macd(macd_5s, ohlc_5s, "alcista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_5s, par, "bajista", macd_5s["MACD"].iloc[-2]))
            seg.start()
            return ""
        else:
            return ""
    else:
        return ""


def analisis_y_estrategia3(ohlc_5s, ohlc_1m, ohlc_5m, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                           sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min):
    ichi_1m = ichimoku(ohlc_1m)
    print(ichi_1m["Senkou span A"].iloc[-26], ohlc_5s['c'].iloc[-1], ichi_1m["Senkou span B"].iloc[-26])
    if (ichi_1m["Senkou span A"].iloc[-26] < ohlc_5s['c'].iloc[-1] < ichi_1m["Senkou span B"].iloc[-26]) or \
            (ichi_1m["Senkou span B"].iloc[-26] < ohlc_5s['c'].iloc[-1] < ichi_1m["Senkou span A"].iloc[-26]):
        bollinger_5s = boll_bnd(ohlc_5s)
        adx_5s = ADX(ohlc_5s, 14)
        rsi_5s = RSI(ohlc_5s, periodo=7)
        print(bollinger_5s["BB_up"].iloc[-1])
        print(bollinger_5s["BB_dn"].iloc[-1])
        if (ohlc_5s['c'].iloc[-1] > bollinger_5s["BB_up"].iloc[-1]) and (adx_5s["ADX"].iloc[-1] < 32.0) and (
                rsi_5s.iloc[-1] < 70):
            return "ventac"
        elif (ohlc_5s['c'].iloc[-1] < bollinger_5s["BB_dn"].iloc[-1]) and (adx_5s["ADX"].iloc[-1] < 32.0) and (
                rsi_5s.iloc[-1] > 30):
            return "comprac"
    if (res_max_1min >= res_min_1min > ohlc_5s['c'].iloc[-1]) and (res_max_5min >= res_min_5min > ohlc_5s['c'].iloc[-1]) \
            and (ichi_1m['Senkou span B'].iloc[-26] < ohlc_5s['c'].iloc[-1] > ichi_1m['Senkou span A'].iloc[-26]):
        ichi_5s = ichimoku(ohlc_5s)
        if ichi_5s['Senkou span B'].iloc[-26] < ohlc_5s['c'].iloc[-1] > ichi_5s['Senkou span A'].iloc[-26]:
            adx_5s = ADX(ohlc_5s, periodos=50)
            rsi_5s = RSI(ohlc_5s, periodo=2)
            if (adx_5s["ADX"].iloc[-1] > 15.0 and adx_5s["DI+"].iloc[-1] > adx_5s["DI-"].iloc[-1]) and \
                    (adx_5s["ADX"].iloc[-2] < adx_5s["ADX"].iloc[-1]):
                if rsi_5s.iloc[-2] < 30.0 and ohlc_5s['c'].iloc[-2] < ohlc_5s['c'].iloc[-1]:
                    return "compraf"
    if (sop_min_1min <= sop_max_1min < ohlc_5s['c'].iloc[-1]) and (sop_min_5min <= sop_max_5min < ohlc_5s['c'].iloc[-1]) \
            and (ichi_1m['Senkou span A'].iloc[-26] > ohlc_5s['c'].iloc[-1] < ichi_1m['Senkou span B'].iloc[-26]):
        ichi_5s = ichimoku(ohlc_5s)
        if ichi_5s['Senkou span B'].iloc[-26] > ohlc_5s['c'].iloc[-1] < ichi_5s['Senkou span A'].iloc[-26]:
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
        else:
            return ""
    else:
        return ""
