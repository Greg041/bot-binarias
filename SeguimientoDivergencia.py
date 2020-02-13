from Ejecucion import ejecucion
import pandas as pd
import time
from ADX import ADX
from macd import MACD


def seguimiento_div(ohlc_1m, ohlc_10s, par, tipo_de_divergencia, punto_max_min_macd, punto_ultimo, monto=None):
    print("estamos en seguimiento divergencia")
    if tipo_de_divergencia == "bajista":
        punto_max_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        while punto_ultimo_macd < punto_max_macd:
            starttime = time.time()
            adx_1m = ADX(ohlc_1m)
            adx_10s = ADX(ohlc_10s)
            try:
                print(adx_1m["ADX"].iloc[-1], adx_10s["DI-"].iloc[-1], adx_10s["DI+"].iloc[-1])
                if adx_1m["ADX"].iloc[-1] < 25.0 and adx_10s["DI-"].iloc[-1] > adx_10s["DI+"].iloc[-1] and \
                        adx_10s["DI-"].iloc[-1] > adx_10s["DI-"].iloc[-2]:
                    ejecucion("ventac", par, '5', monto)
                    break
                else:
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        punto_ultimo_macd = MACD(ohlc_10s)["MACD"].iloc[-1]
                    except:
                        print("reintentando lectura ohlc_10s")
                time.sleep(10 - ((time.time() - starttime) % 10))
            except:
                print("Hubo error en calculo de adx")
                print(adx_10s)
                print(adx_1m)
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd < punto_max_macd, punto_ultimo_macd, punto_max_macd)
    elif tipo_de_divergencia == "alcista":
        punto_min_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        while punto_ultimo_macd > punto_min_macd:
            starttime = time.time()
            adx_1m = ADX(ohlc_1m)
            adx_10s = ADX(ohlc_10s)
            try:
                print(adx_1m["ADX"].iloc[-1], adx_10s["DI+"].iloc[-1], adx_10s["DI-"].iloc[-1])
                if adx_1m["ADX"].iloc[-1] < 25.0 and adx_10s["DI+"].iloc[-1] > adx_10s["DI-"].iloc[-1] and \
                        adx_10s["DI+"].iloc[-1] > adx_10s["DI+"].iloc[-2]:
                    ejecucion("comprac", par, '5', monto)
                    break
                else:
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        punto_ultimo_macd = MACD(ohlc_10s)["MACD"].iloc[-1]
                    except:
                        print("reintentando lectura ohlc_10s")
                time.sleep(10 - ((time.time() - starttime) % 10))
            except:
                print("hubo error en calculo de adx")
                print(adx_10s)
                print(adx_1m)
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd > punto_min_macd, punto_ultimo_macd, punto_min_macd)
