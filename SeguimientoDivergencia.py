from Ejecucion import ejecucion
import pandas as pd
import time
from ADX import ADX
from macd import MACD


def seguimiento_div(ohlc_1m, ohlc_5s, par, tipo_de_divergencia, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m,
                         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m):
    print("estamos en seguimiento divergencia")
    if tipo_de_divergencia == "bajista":
        punto_max_macd = MACD(ohlc_5s)["MACD"].iloc[-2]
        punto_ultimo_macd = MACD(ohlc_5s)["MACD"].iloc[-1]
        while punto_ultimo_macd < punto_max_macd:
            adx_1m = ADX(ohlc_1m)
            adx_5s = ADX(ohlc_5s)
            print(adx_1m["ADX"].iloc[-1], adx_5s["DI-"].iloc[-1], adx_5s["DI+"].iloc[-1])
            if adx_1m["ADX"].iloc[-1] < 25.0 and adx_5s["DI-"].iloc[-1] > adx_5s["DI+"].iloc[-1] and \
                    adx_5s["DI-"].iloc[-1] > adx_5s["DI-"].iloc[-2]:
                ejecucion("ventac", par)
                break
            else:
                try:
                    ohlc_5s = pd.read_csv("datos_5s.csv", index_col="time")
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    punto_ultimo_macd = MACD(ohlc_5s)["MACD"].iloc[-1]
                except:
                    print("reintentando lectura ohlc_5s")
            time.sleep(5)
        print("Se sale del seguimiento porque se ejecuto o",
              res_max_1m > ohlc_5s['c'].iloc[-1] > res_min_1m or res_max_5m > ohlc_5s['c'].iloc[-1] > res_min_5m)
    elif tipo_de_divergencia == "alcista":
        punto_min_macd = MACD(ohlc_5s)["MACD"].iloc[-2]
        punto_ultimo_macd = MACD(ohlc_5s)["MACD"].iloc[-1]
        while punto_ultimo_macd > punto_min_macd:
            adx_1m = ADX(ohlc_1m)
            adx_5s = ADX(ohlc_5s)
            print(adx_1m["ADX"].iloc[-1], adx_5s["DI+"].iloc[-1], adx_5s["DI-"].iloc[-1])
            if adx_1m["ADX"].iloc[-1] < 25.0 and adx_5s["DI+"].iloc[-1] > adx_5s["DI-"].iloc[-1] and \
                    adx_5s["DI+"].iloc[-1] > adx_5s["DI+"].iloc[-2]:
                ejecucion("comprac", par)
                break
            else:
                try:
                    ohlc_5s = pd.read_csv("datos_5s.csv", index_col="time")
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    punto_ultimo_macd = MACD(ohlc_5s)["MACD"].iloc[-1]
                except:
                    print("reintentando lectura ohlc_5s")
            time.sleep(5)
        print("Se sale del seguimiento porque se ejecuto o",
              sop_min_1m < ohlc_5s['c'].iloc[-1] < sop_max_1m or sop_min_5m < ohlc_5s['c'].iloc[-1] < sop_max_5m)
