from ADX import ADX
from RSI import RSI
from ichimoku import ichimoku
from macd import MACD, detectar_div_macd, detectar_div_historigrama
from multiprocessing import Process
from SeguimientoIchimoku import seguimiento_ichimoku, seguimiento_ichimoku2
from BollingerBands import boll_bnd
from SeguimientoDivergencia import seguimiento_div
from Ejecucion import ejecucion
import time


def engulfing(ohlc_vela_anterior, ohlc_vela_actual, alcista_o_bajista: str) -> bool:
    if alcista_o_bajista == "alcista":
        print("close vela anterior:", ohlc_vela_anterior['c'], "open vela anterior:", ohlc_vela_anterior['o'],
              "close vela actual:", ohlc_vela_actual['c'])
        return (ohlc_vela_anterior['c'] <= ohlc_vela_anterior['o']) and (
                ohlc_vela_actual['c'] >= ohlc_vela_anterior['h'])
    elif alcista_o_bajista == "bajista":
        print("close vela anterior:", ohlc_vela_anterior['c'], "open vela anterior:", ohlc_vela_anterior['o'],
              "close vela actual:", ohlc_vela_actual['c'])
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


def analisis_y_estrategia(ohlc_10s, ohlc_1m, ohlc_5m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                          sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, res_max_30m, res_min_30m, sop_min_30m,
                          sop_max_30m, monto, client):
    ichi_1m = ichimoku(ohlc_1m)
    macd_1m = MACD(ohlc_1m)
    adx_1m = ADX(ohlc_1m)
    rsi_1m = RSI(ohlc_1m)
    ichi_5m = ichimoku(ohlc_5m)
    adx_5m = ADX(ohlc_5m)
    rsi_5m = RSI(ohlc_5m)
    print((ichi_5m["Senkou span A"].iloc[-26] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]),
          (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0),
          (adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1]), (70.0 > rsi_5m.iloc[-1] > rsi_5m.iloc[-2]))
    print((ichi_5m["Senkou span A"].iloc[-26] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]),
          (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0),
          (adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1]), (rsi_5m.iloc[-2] > rsi_5m.iloc[-1] > 30.0))
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
            > ichi_1m["kijun-sen"].iloc[-1]) and \
                (ichi_1m["Senkou span A"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span B"].iloc[-26] or
                 ichi_1m["Senkou span B"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span A"].iloc[-26] or
                 ichi_1m["Senkou span A"].iloc[-26] < ohlc_1m['c'].iloc[-1] > ichi_1m["Senkou span B"].iloc[-26]) and \
                (ichi_1m["Senkou span A"].iloc[-2] <= ichi_1m["Senkou span A"].iloc[-1]):
            seguimiento_ichimoku(ohlc_10s, ohlc_1m, ohlc_5m, ichi_1m, par, "compraf", res_max_30m, res_min_30m,
                                 sop_min_30m, sop_max_30m, res_max_5min, res_min_5min,
                                 sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                 sop_min_1min, sop_max_1min, monto, client)
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
            < ichi_1m["kijun-sen"].iloc[-1]) and \
                (ichi_1m["Senkou span A"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span B"].iloc[-26] or
                 ichi_1m["Senkou span B"].iloc[-26] <= ohlc_1m['c'].iloc[-1] <= ichi_1m["Senkou span A"].iloc[-26] or
                 ichi_1m["Senkou span A"].iloc[-26] > ohlc_1m['c'].iloc[-1] < ichi_1m["Senkou span B"].iloc[-26]) and \
                (ichi_1m["Senkou span A"].iloc[-2] >= ichi_1m["Senkou span A"].iloc[-1]):
            seguimiento_ichimoku(ohlc_10s, ohlc_1m, ohlc_5m, ichi_1m, par, "ventaf", res_max_30m, res_min_30m,
                                 sop_min_30m, sop_max_30m, res_max_5min, res_min_5min,
                                 sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                 sop_min_1min, sop_max_1min, monto, client)
            return ""
    # estrategia #2 divergencias
    if adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI+"].iloc[-1] > adx_1m["DI-"].iloc[-1]:
        print("en res 1 min", res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min)
        print("en res 5 min", res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min)
        if (res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min or res_max_5min > ohlc_10s['c'].iloc[
            -1] > res_min_5min) \
                and detectar_div_macd(macd_1m, ohlc_1m, "bajista") and detectar_div_historigrama(macd_1m, ohlc_1m,
                                                                                                 "bajista"):
            fichero_div = open("datos divergencias.txt", "at")
            fichero_div.write(f"\nen res 1 min: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                              f"en res 5 min: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                              f"en res 30 min: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n")
            fichero_div.close()
            seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "bajista", macd_1m["MACD"].iloc[-2],
                            macd_1m["MACD"].iloc[-1], monto, client)
            return ""
        else:
            return ""
    elif adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI-"].iloc[-1] > adx_1m["DI+"].iloc[-1]:
        print("en sop 1 min", sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min)
        print("en sop 5 min", sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min)
        if (sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min or sop_min_5min < ohlc_10s['c'].iloc[
            -1] < sop_max_5min) \
                and detectar_div_macd(macd_1m, ohlc_1m, "alcista") and detectar_div_historigrama(macd_1m, ohlc_1m,
                                                                                                 "alcista"):
            fichero_div = open("datos divergencias.txt", "at")
            fichero_div.write(f"\nen sop 1 min: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                              f"en sop 5 min: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                              f"en sop 30 min: {sop_min_30m > ohlc_10s['c'].iloc[-1] > sop_max_30m} \n")
            fichero_div.close()
            seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, "alcista", macd_1m["MACD"].iloc[-2],
                            macd_1m["MACD"].iloc[-1], monto, client)
            return ""
        else:
            return ""
    # estrategia #3 seguimiento de tendencia consolidada
    if (ichi_5m["Senkou span A"].iloc[-26] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]) and \
            (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0) and \
            (adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1]) and (70.0 > rsi_5m.iloc[-1] > rsi_5m.iloc[-2]):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-26] < ohlc_1m['c'].iloc[-1] > ichimoku_1m["Senkou span A"].iloc[-26] and
            ichimoku_1m["Senkou span B"].iloc[-27] < ohlc_1m['c'].iloc[-2] > ichimoku_1m["Senkou span A"].iloc[-27]) and \
                ((engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], "alcista")) or
                 (setenta_por_ciento(ohlc_1m.iloc[-3], "bajista") and ohlc_1m['o'].iloc[-2] >= ohlc_1m['c'].iloc[-2] and \
                  setenta_por_ciento(ohlc_1m.iloc[-1], "alcista"))) and \
                (adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1]) and (rsi_1m.iloc[-1] > rsi_1m.iloc[-2]) and \
                (ichi_1m["tenkan-sen"].iloc[-1] > ichi_1m["kijun-sen"].iloc[-1]):
            fichero_est_3 = open("datos estrategia 3.txt", "at")
            fichero_est_3.write(f"\nengulfing: {engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], 'alcista')}")
            fichero_est_3.close()
            seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, "compraf", res_max_30m, res_min_30m, sop_min_30m,
                                  sop_max_30m, res_max_5min, res_min_5min,
                                  sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                  sop_min_1min, sop_max_1min, monto, client)
            return ""
        else:
            return ""
    elif (ichi_5m["Senkou span A"].iloc[-26] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]) and \
            (adx_5m["ADX"].iloc[-2] < adx_5m["ADX"].iloc[-1] > 20.0) and \
            (adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1]) and (rsi_5m.iloc[-2] > rsi_5m.iloc[-1] > 30.0):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-26] > ohlc_1m['c'].iloc[-1] < ichimoku_1m["Senkou span A"].iloc[-26] and
            ichimoku_1m["Senkou span B"].iloc[-27] > ohlc_1m['c'].iloc[-2] < ichimoku_1m["Senkou span A"].iloc[-27]) and \
                ((engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], "bajista")) or
                 (setenta_por_ciento(ohlc_1m.iloc[-3], "alcista") and ohlc_1m['o'].iloc[-2] <= ohlc_1m['c'].iloc[-2] and \
                  setenta_por_ciento(ohlc_1m.iloc[-1], "bajista"))) and \
                (adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1]) and (rsi_1m.iloc[-1] < rsi_1m.iloc[-2]) and \
                (ichi_1m["tenkan-sen"].iloc[-1] < ichi_1m["kijun-sen"].iloc[-1]):
            fichero_est_3 = open("datos estrategia 3.txt", "at")
            fichero_est_3.write(f"\nengulfing: {engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], 'bajista')}")
            fichero_est_3.close()
            seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, "ventaf", res_max_30m, res_min_30m, sop_min_30m,
                                  sop_max_30m, res_max_5min, res_min_5min,
                                  sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                  sop_min_1min, sop_max_1min, monto, client)
            return ""
        else:
            return ""
    # estrategia #4
    if (ichi_5m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]) or \
            (ichi_5m["Senkou span B"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichi_5m["Senkou span A"].iloc[-26]):
        bollinger_1m = boll_bnd(ohlc_1m)
        adx_1m = ADX(ohlc_1m, 14)
        rsi_1m = RSI(ohlc_1m, periodo=7)
        print(bollinger_1m["BB_up"].iloc[-1])
        print(bollinger_1m["BB_dn"].iloc[-1])
        print(ohlc_10s['c'].iloc[-1])
        print(ohlc_10s['c'].iloc[-1] < bollinger_1m["BB_dn"].iloc[-1])
        print("en resistencia ", res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min,
              res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min, res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m)
        print("en soporte ", sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min,
              sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min, sop_min_30m < ohlc_10s['c'].iloc[-1] < sop_max_30m)
        if (ohlc_10s['c'].iloc[-1] > bollinger_1m["BB_up"].iloc[-1]) and (adx_1m["ADX"].iloc[-1] < 32.0) and (
                rsi_1m.iloc[-1] < 70) and ((res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min and
                                           sop_min_5min < ohlc_10s['c'].iloc[-1] > sop_max_5min and
                                           sop_max_30m < ohlc_10s['c'].iloc[-1] > sop_min_30m) or
                (res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min and
                 sop_min_30m < ohlc_10s['c'].iloc[-1] > sop_max_30m) or
                res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m):
            ejecucion("ventac", par, '4', monto)
            fichero_est_4 = open("datos estrategia 4.txt", "at")
            fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                f"en resistencia 1m: {res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min} \n"
                                f"en resistencia 5m: {res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min} \n"
                                f"en resistencia 30m: {res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m} \n"
                                f"venta \n")
            fichero_est_4.close()
            time.sleep(120)
        elif (ohlc_10s['c'].iloc[-1] < bollinger_1m["BB_dn"].iloc[-1]) and (adx_1m["ADX"].iloc[-1] < 32.0) and (
                rsi_1m.iloc[-1] > 30) and ((sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min and
                                           res_max_5min > ohlc_10s['c'].iloc[-1] < res_min_5min and
                                           res_max_30m > ohlc_10s['c'].iloc[-1] < res_min_30m) or
                (sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min and
                 res_max_30m > ohlc_10s['c'].iloc[-1] < res_min_30m) or
                sop_min_30m < ohlc_10s['c'].iloc[-1] < sop_max_30m):
            ejecucion("comprac", par, '4', monto)
            fichero_est_4 = open("datos estrategia 4.txt", "at")
            fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                f"en soporte 1m: {sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min} \n"
                                f"en soporte 5m: {sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min} \n"
                                f"en soporte 30m: {sop_min_30m < ohlc_10s['c'].iloc[-1] < sop_max_30m} \n"
                                f"compra \n")
            fichero_est_4.close()
            time.sleep(120)


def analisis_y_estrategia_favor(ohlc_10s, ohlc_1m, ohlc_5m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                                sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, monto):
    ichi_5m = ichimoku(ohlc_5m)
    adx_5m = ADX(ohlc_5m)
    rsi_5m = RSI(ohlc_5m)
    print(ichi_5m["Senkou span A"].iloc[-1] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-1],
          adx_5m["ADX"].iloc[-1] > 20.0 and adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1], rsi_5m.iloc[-1] < 70.0)
    print(ichi_5m["Senkou span A"].iloc[-1] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-1],
          adx_5m["ADX"].iloc[-1] > 20.0 and adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1], rsi_5m.iloc[-1] > 30.0)
    if (ichi_5m["Senkou span A"].iloc[-1] < ohlc_5m['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-1]) and \
            (adx_5m["ADX"].iloc[-1] > 20.0 and adx_5m["DI+"].iloc[-1] > adx_5m["DI-"].iloc[-1]) and \
            (rsi_5m.iloc[-1] < 70.0) and (res_max_5min >= res_min_5min > ohlc_10s['c'].iloc[-1]):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-1] < ohlc_10s['c'].iloc[-1] > ichimoku_1m["Senkou span A"].iloc[-1]) and \
                engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], "alcista"):
            seg = Process(target=seguimiento_ichimoku2, args=(ohlc_5m, ohlc_1m, ohlc_10s, par, "compraf",
                                                              res_max_5min, res_min_5min,
                                                              sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                              sop_min_1min, sop_max_1min, monto))
            seg.start()
            time.sleep(120)
            return ""
        else:
            return ""
    elif (ichi_5m["Senkou span A"].iloc[-1] > ohlc_5m['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-1]) and \
            (adx_5m["ADX"].iloc[-1] > 20.0 and adx_5m["DI-"].iloc[-1] > adx_5m["DI+"].iloc[-1]) and \
            (rsi_5m.iloc[-1] > 30.0) and (sop_min_5min <= sop_max_5min < ohlc_10s['c'].iloc[-1]):
        ichimoku_1m = ichimoku(ohlc_1m)
        if (ichimoku_1m["Senkou span B"].iloc[-1] > ohlc_10s['c'].iloc[-1] < ichimoku_1m["Senkou span A"].iloc[-1]) and \
                engulfing(ohlc_1m.iloc[-2], ohlc_1m.iloc[-1], "bajista"):
            seg = Process(target=seguimiento_ichimoku2, args=(ohlc_5m, ohlc_1m, ohlc_10s, par, "compraf",
                                                              res_max_5min, res_min_5min,
                                                              sop_min_5min, sop_max_5min, res_max_1min, res_min_1min,
                                                              sop_min_1min, sop_max_1min, monto))
            seg.start()
            time.sleep(120)
            return ""
        else:
            return ""
    else:
        return ""


def analisis_y_estrategia_contra(ohlc_10s, ohlc_1m, par, res_max_1min, res_min_1min, res_max_5min, res_min_5min,
                                 sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, monto):
    adx_1m = ADX(ohlc_1m)
    macd_10s = MACD(ohlc_10s)
    print("en res 1 min", res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min)
    print("en res 5 min", res_max_5min > ohlc_10s['c'].iloc[-1] > res_min_5min)
    print("en sop 1 min", sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min)
    print("en sop 5 min", sop_min_5min < ohlc_10s['c'].iloc[-1] < sop_max_5min)
    if adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI+"].iloc[-1] > adx_1m["DI-"].iloc[-1]:
        if (res_max_1min > ohlc_10s['c'].iloc[-1] > res_min_1min or res_max_5min > ohlc_10s['c'].iloc[
            -1] > res_min_5min) \
                and detectar_div_macd(macd_10s, ohlc_10s, "bajista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_10s, par, "bajista", macd_10s["MACD"].iloc[-2],
                                                        macd_10s["MACD"].iloc[-1], monto))
            seg.start()
            return ""
        else:
            return ""
    elif adx_1m["ADX"].iloc[-1] > 25.0 and adx_1m["DI-"].iloc[-1] > adx_1m["DI+"].iloc[-1]:
        if (sop_min_1min < ohlc_10s['c'].iloc[-1] < sop_max_1min or sop_min_5min < ohlc_10s['c'].iloc[
            -1] < sop_max_5min) \
                and detectar_div_macd(macd_10s, ohlc_10s, "alcista"):
            seg = Process(target=seguimiento_div, args=(ohlc_1m, ohlc_10s, par, "alcista", macd_10s["MACD"].iloc[-2],
                                                        macd_10s["MACD"].iloc[-1], monto))
            seg.start()
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
