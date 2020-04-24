from ADX import ADX
from RSI import RSI
from ichimoku import ichimoku
from macd import MACD, detectar_div_macd, detectar_div_historigrama
from SeguimientoIchimoku import seguimiento_ichimoku, seguimiento_ichimoku2
from BollingerBands import boll_bnd
from SeguimientoDivergencia import seguimiento_div
from Ejecucion import ejecucion
from seguimiento_bollinger import seguimiento_boll
import time
import pandas as pd


def engulfing(ohlc_vela_anterior, ohlc_vela_actual, alcista_o_bajista: str) -> bool:
    if alcista_o_bajista == "alcista":
        print("open vela anterior:", ohlc_vela_anterior['o'], "close vela anterior:", ohlc_vela_anterior['c'],
              "open vela actual:", ohlc_vela_actual['c'], "close vela actual:", ohlc_vela_actual['c'])
        return (ohlc_vela_anterior['c'] <= ohlc_vela_anterior['o']) and (
                ohlc_vela_actual['c'] >= ohlc_vela_anterior['h'])
    elif alcista_o_bajista == "bajista":
        print("open vela anterior:", ohlc_vela_anterior['o'], "close vela anterior:", ohlc_vela_anterior['c'],
              "open vela actual:", ohlc_vela_actual['c'], "close vela actual:", ohlc_vela_actual['c'])
        return (ohlc_vela_anterior['c'] >= ohlc_vela_anterior['o']) and (
                ohlc_vela_actual['c'] <= ohlc_vela_anterior['l'])


# Calcula si el cierre de una vela es mayor o menor al 70% del recorrido total de la vela dependiendo de si es alcista
# o bajista
def setenta_por_ciento(ohlc_vela, alcista_o_bajista: str) -> bool:
    if alcista_o_bajista == "alcista":
        if ohlc_vela['o'] < ohlc_vela['c']:
            print(f"open: {ohlc_vela['o']},  high: {ohlc_vela['h']}, close: {ohlc_vela['c']}")
            return (((ohlc_vela['h'] - ohlc_vela['o']) * 70) / 100) <= (ohlc_vela['c'] - ohlc_vela['o'])
    elif alcista_o_bajista == "bajista":
        if ohlc_vela['o'] > ohlc_vela['c']:
            print(
                f"open: {ohlc_vela['o']},  low: {ohlc_vela['l']}, close: {ohlc_vela['c']}")
            return (((ohlc_vela['l'] - ohlc_vela['o']) * 70) / 100) >= (ohlc_vela['c'] - ohlc_vela['o'])


def analisis_y_estrategia(ohlc_10s, ohlc_1m, ohlc_5m, ohlc_30m, par, res_max_1min, res_min_1min, res_max_5min,
                          res_min_5min,
                          sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, res_max_30m, res_min_30m, sop_min_30m,
                          sop_max_30m, monto, client, request):

    ichi_1m = ichimoku(ohlc_1m)
    macd_1m = MACD(ohlc_1m)
    adx_1m = ADX(ohlc_1m)
    rsi_1m = RSI(ohlc_1m)
    ichi_5m = ichimoku(ohlc_5m)
    adx_5m = ADX(ohlc_5m)
    rsi_5m = RSI(ohlc_5m)
    ichi_30m = ichimoku(ohlc_30m)
    ichimoku_10s = ichimoku(ohlc_10s)
    print((ichi_5m["Senkou span A"].iloc[-26] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]),
          (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0),
          (adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1]), (rsi_5m.iloc[-1] > rsi_5m.iloc[-2]))
    print((ichi_5m["Senkou span A"].iloc[-26] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]),
          (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0),
          (adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1]), (rsi_5m.iloc[-2] > rsi_5m.iloc[-1]))
    # estrategia #1 predicción de comienzo de tendencia
    if (ichi_5m["Senkou span A"].iloc[-26] <= ohlc_5m['o'].iloc[-1] <= ichi_5m["Senkou span B"].iloc[-26] or
        ichi_5m["Senkou span B"].iloc[-26] <= ohlc_5m['o'].iloc[-1] <= ichi_5m["Senkou span A"].iloc[-26]) and \
            ichi_5m["Senkou span A"].iloc[-26] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]:
        print("estrategia 1 fase 2 compra")
        print(f"tenkan-sen: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]}")
        print(f"kijun-sen: {ichi_1m['kijun-sen'].iloc[-1]}")
        print(f"precio: {ohlc_1m['c'].iloc[-1]}")
        print(f"senkou span A y B -26: {ichi_1m['Senkou span A'].iloc[-26]}, {ichi_1m['Senkou span B'].iloc[-26]}")
        print(f"senkou span A -1: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]}")
        if (ichi_1m["tenkan-sen"].iloc[-2] <= ichi_1m["tenkan-sen"].iloc[-1] and ichi_1m["tenkan-sen"].iloc[-1]
            >= ichi_1m["kijun-sen"].iloc[-1]) and \
                (ichi_1m["Senkou span A"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span B"].iloc[-26] or
                 ichi_1m["Senkou span B"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span A"].iloc[-26] or
                 ichi_1m["Senkou span A"].iloc[-26] < ohlc_1m['c'].iloc[-1] > ichi_1m["Senkou span B"].iloc[-26]) and \
                (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span A"].iloc[-1]):
            if res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min or res_max_30m > ohlc_10s['c'].iloc[
                -1] > res_min_30m:
                print("Se encuentra en una resistencia fuerte")
                pass
            else:
                seguimiento_ichimoku(ohlc_10s, ohlc_1m, ohlc_5m, ichi_1m, par, "compraf", res_max_30m, res_min_30m,
                                     sop_min_30m, sop_max_30m, res_max_5min, res_min_5min,
                                     sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                     sop_min_1min, sop_max_1min, monto, client, request)
    elif (ichi_5m["Senkou span A"].iloc[-26] <= ohlc_5m['o'].iloc[-1] <= ichi_5m["Senkou span B"].iloc[-26] or
          ichi_5m["Senkou span B"].iloc[-26] <= ohlc_5m['o'].iloc[-1] <= ichi_5m["Senkou span A"].iloc[-26]) and \
            ichi_5m["Senkou span A"].iloc[-26] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]:
        print("estrategia 1 fase 2 venta")
        print(f"tenkan-sen: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]}")
        print(f"kijun-sen: {ichi_1m['kijun-sen'].iloc[-1]}")
        print(f"precio: {ohlc_1m['c'].iloc[-1]}")
        print(f"senkou span A y B -26: {ichi_1m['Senkou span A'].iloc[-26]}, {ichi_1m['Senkou span B'].iloc[-26]}")
        print(f"senkou span A -1: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]}")
        if (ichi_1m["tenkan-sen"].iloc[-2] >= ichi_1m["tenkan-sen"].iloc[-1] and ichi_1m["tenkan-sen"].iloc[-1]
            <= ichi_1m["kijun-sen"].iloc[-1]) and \
                (ichi_1m["Senkou span A"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span B"].iloc[-26] or
                 ichi_1m["Senkou span B"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span A"].iloc[-26] or
                 ichi_1m["Senkou span A"].iloc[-26] > ohlc_1m['c'].iloc[-1] < ichi_1m["Senkou span B"].iloc[-26]) and \
                (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span A"].iloc[-1]):
            if sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min or sop_min_30m < ohlc_10s['c'].iloc[
                -1] < sop_max_30m:
                print("Se encuentra en un soporte fuerte")
                pass
            else:
                seguimiento_ichimoku(ohlc_10s, ohlc_1m, ohlc_5m, ichi_1m, par, "ventaf", res_max_30m, res_min_30m,
                                     sop_min_30m, sop_max_30m, res_max_5min, res_min_5min,
                                     sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                     sop_min_1min, sop_max_1min, monto, client, request)
    # estrategia #2 divergencias
    if adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI+"].iloc[-1] > adx_1m["DI-"].iloc[-1]:
        print("en res 1 min", ohlc_10s['c'].iloc[-1] > res_min_1min)
        print("en res 5 min", ohlc_10s['c'].iloc[-1] > res_min_5min)
        if res_min_1min != res_min_1min:
            if (res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min) and detectar_div_macd(macd_1m, ohlc_1m, "bajista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "bajista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen res 1 min: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                                      f"en res 5 min: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                                      f"en res 30 min: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "bajista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        else:
            if ohlc_10s['c'].iloc[-1] > res_min_1min and detectar_div_macd(macd_1m, ohlc_1m, "bajista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "bajista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen res 1 min: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                                      f"en res 5 min: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                                      f"en res 30 min: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "bajista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        if res_min_5min != res_max_5min:
            if res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min and detectar_div_macd(macd_1m, ohlc_1m, "bajista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "bajista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen res 1 min: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                                      f"en res 5 min: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                                      f"en res 30 min: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "bajista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        else:
            if ohlc_10s['c'].iloc[-1] > res_min_5min and detectar_div_macd(macd_1m, ohlc_1m, "bajista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "bajista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen res 1 min: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                                      f"en res 5 min: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                                      f"en res 30 min: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "bajista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
    elif adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI-"].iloc[-1] > adx_1m["DI+"].iloc[-1]:
        print("en sop 1 min", ohlc_10s['c'].iloc[-1] < sop_max_1min)
        print("en sop 5 min", ohlc_10s['c'].iloc[-1] < sop_max_5min)
        if sop_max_1min != sop_min_1min:
            if sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min and detectar_div_macd(macd_1m, ohlc_1m, "alcista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "alcista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen sop 1 min: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                                      f"en sop 5 min: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                                      f"en sop 30 min: {sop_min_30m > ohlc_10s['c'].iloc[-1] > sop_max_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "alcista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        else:
            if ohlc_10s['c'].iloc[-1] < sop_max_1min and detectar_div_macd(macd_1m, ohlc_1m, "alcista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "alcista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen sop 1 min: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                                      f"en sop 5 min: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                                      f"en sop 30 min: {sop_min_30m > ohlc_10s['c'].iloc[-1] > sop_max_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "alcista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        if sop_max_5min != sop_min_5min:
            if sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min and detectar_div_macd(macd_1m, ohlc_1m, "alcista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "alcista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen sop 1 min: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                                      f"en sop 5 min: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                                      f"en sop 30 min: {sop_min_30m > ohlc_10s['c'].iloc[-1] > sop_max_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "alcista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
        else:
            if ohlc_10s['c'].iloc[-1] < sop_max_5min and detectar_div_macd(macd_1m, ohlc_1m, "alcista") \
                    and detectar_div_historigrama(macd_1m, ohlc_1m, "alcista"):
                with open("datos divergencias.txt", "at") as fichero_div:
                    fichero_div.write(f"\nen sop 1 min: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                                      f"en sop 5 min: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                                      f"en sop 30 min: {sop_min_30m > ohlc_10s['c'].iloc[-1] > sop_max_30m} \n")
                seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "alcista", macd_1m["MACD"].iloc[-2],
                                macd_1m["MACD"].iloc[-1], monto, client, request)
    # estrategia #3 seguimiento de tendencia consolidada
    if (ichi_5m["Senkou span A"].iloc[-26] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]) and \
            (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0) and \
            (adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1]) and (rsi_5m.iloc[-1] > rsi_5m.iloc[-2]):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-26] < ohlc_1m['c'].iloc[-1] > ichimoku_1m["Senkou span A"].iloc[-26] and
            ichimoku_1m["Senkou span B"].iloc[-27] < ohlc_1m['c'].iloc[-2] > ichimoku_1m["Senkou span A"].iloc[-27]) and \
                (setenta_por_ciento(ohlc_1m.iloc[-3], "bajista") and ohlc_1m['o'].iloc[-2] >= ohlc_1m['c'].iloc[-2] and \
                 setenta_por_ciento(ohlc_1m.iloc[-1], "alcista")) and \
                (adx_1m["ADX"].iloc[-2] <= adx_1m["ADX"].iloc[-1]) and (rsi_1m.iloc[-1] > rsi_1m.iloc[-2]) and \
                (ichi_1m["tenkan-sen"].iloc[-1] >= ichi_1m["kijun-sen"].iloc[-1]):
            if res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min or res_max_30m > ohlc_10s['c'].iloc[
                -1] > res_min_30m:
                print("Se encuentra en una resistencia fuerte")
                pass
            else:
                with open("datos estrategia 3.txt", "at") as fichero_est_3:
                    fichero_est_3.write(f"\nengulfing: {engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], 'alcista')}")
                seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, "compraf", res_max_30m, res_min_30m, sop_min_30m,
                                      sop_max_30m, res_max_5min, res_min_5min,
                                      sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                      sop_min_1min, sop_max_1min, monto, client, request)
    elif (ichi_5m["Senkou span A"].iloc[-26] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]) and \
            (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0) and \
            (adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1]) and (rsi_5m.iloc[-2] > rsi_5m.iloc[-1]):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-26] > ohlc_1m['c'].iloc[-1] < ichimoku_1m["Senkou span A"].iloc[-26] and
            ichimoku_1m["Senkou span B"].iloc[-27] > ohlc_1m['c'].iloc[-2] < ichimoku_1m["Senkou span A"].iloc[-27]) and \
                (setenta_por_ciento(ohlc_1m.iloc[-3], "alcista") and ohlc_1m['o'].iloc[-2] <= ohlc_1m['c'].iloc[-2] and \
                 setenta_por_ciento(ohlc_1m.iloc[-1], "bajista")) and \
                (adx_1m["ADX"].iloc[-2] <= adx_1m["ADX"].iloc[-1]) and (rsi_1m.iloc[-1] < rsi_1m.iloc[-2]) and \
                (ichi_1m["tenkan-sen"].iloc[-1] <= ichi_1m["kijun-sen"].iloc[-1]):
            if sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min or sop_min_30m < ohlc_10s['c'].iloc[
                -1] < sop_max_30m:
                print("Se encuentra en un soporte fuerte")
                pass
            else:
                with open("datos estrategia 3.txt", "at") as fichero_est_3:
                    fichero_est_3.write(f"\nengulfing: {engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], 'bajista')}")
                seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, "ventaf", res_max_30m, res_min_30m, sop_min_30m,
                                      sop_max_30m, res_max_5min, res_min_5min,
                                      sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                      sop_min_1min, sop_max_1min, monto, client, request)
    # estrategia #4
    if (ichi_30m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_30m["Senkou span B"].iloc[-26]) or \
            (ichi_30m["Senkou span B"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_30m["Senkou span A"].iloc[-26]) or \
            (ichi_5m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]) or \
            (ichi_5m["Senkou span B"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_5m["Senkou span A"].iloc[-26]):
        bollinger_1m = boll_bnd(ohlc_1m)
        adx_1m = ADX(ohlc_1m, 14)
        rsi_1m = RSI(ohlc_1m, periodo=7)
        print(bollinger_1m["BB_up"].iloc[-1])
        print(bollinger_1m["BB_dn"].iloc[-1])
        print(ohlc_10s['c'].iloc[-1])
        print("en resistencia ", res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min,
              res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min, res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m)
        print("en soporte ", sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min,
              sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min, sop_min_30m < ohlc_10s['c'].iloc[-1] < sop_max_30m)
        if (ohlc_10s['c'].iloc[-1] > bollinger_1m["BB_up"].iloc[-1]) and (adx_1m["ADX"].iloc[-1] < 32.0) and (
                rsi_1m.iloc[-1] < 70) and (
                ((res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min or res_max_1min <= ohlc_10s['c'].iloc[-1]) and
                 sop_min_5min < ohlc_10s['c'].iloc[-1] > sop_max_5min and
                 sop_max_30m < ohlc_10s['c'].iloc[-1] > sop_min_30m) or
                ((res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min or res_max_5min <= ohlc_10s['c'].iloc[-1]) and
                 sop_min_30m < ohlc_10s['c'].iloc[-1] > sop_max_30m) or
                (res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m)):
            seguimiento_boll(ohlc_5m, ohlc_1m, ohlc_10s, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                             res_max_30m, res_min_30m, sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min,
                             sop_min_30m, sop_max_30m, bollinger_1m, "ventac", par, monto, client, request)
        elif (ohlc_10s['c'].iloc[-1] < bollinger_1m["BB_dn"].iloc[-1]) and (adx_1m["ADX"].iloc[-1] < 32.0) and (
                rsi_1m.iloc[-1] > 30) and (
                ((sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min or ohlc_10s['c'].iloc[-1] <= sop_min_1min) and
                 (res_max_5min > ohlc_10s['c'].iloc[-1] < res_min_5min) and
                 res_max_30m > ohlc_10s['c'].iloc[-1] < res_min_30m) or
                ((sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min or ohlc_10s['c'].iloc[-1] <= sop_min_5min) and
                 res_max_30m > ohlc_10s['c'].iloc[-1] < res_min_30m) or
                sop_min_30m < ohlc_10s['c'].iloc[-1] < sop_max_30m):
            seguimiento_boll(ohlc_5m, ohlc_1m, ohlc_10s, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                             res_max_30m, res_min_30m, sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min,
                             sop_min_30m, sop_max_30m, bollinger_1m, "comprac", par, monto, client, request)
