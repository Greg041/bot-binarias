from ichimoku import ichimoku
from Ejecucion import ejecucion
import pandas as pd
import time


def seguimiento_ichimoku(ohlc_1m, ichimoku_1m, par, tipo_de_operacion, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m):
    print("estamos en seguimiento")
    if tipo_de_operacion == "compraf":
        while ichimoku_1m["Senkou span A"].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[-1]:
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            try:
                ohlc_5s = pd.read_csv("datos_5s.csv", index_col="time")
            except:
                print("reintentando lectura ohlc_5s")
            if res_max_5m > ohlc_5s['c'].iloc[-1] > res_min_5m:
                print("Se encuentra en resistencia")
                time.sleep(60)
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_5s = ichimoku(ohlc_5s)
                if (ichi_5s["Senkou span A"].iloc[-26] < ohlc_5s["c"].iloc[-1] > ichi_5s["Senkou span B"].iloc[-26]) and \
                        (ichi_5s["tenkan-sen"].iloc[-2] <= ichi_5s["kijun-sen"].iloc[-2] and
                         ichi_5s["tenkan-sen"].iloc[-1] > ichi_5s["kijun-sen"].iloc[-1]):
                    ejecucion("compraf", par)
                    break
                # Se verifica que el dataframe esté actualizado tomando en cuenta el minutoa actual y el ultimo
                # minuto del dataframe
                if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                    ohlc_1m.iloc[-1].name[14:16]) and \
                        (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16])):02}" !=
                         ohlc_1m.iloc[-1].name[14:16]):
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                time.sleep(5 - ((time.time() - starttime) % 5))
        print("se sale del seguimiento porque se ejecutó operacion ó",
              ichimoku_1m["Senkou span A"].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[-1])
    elif tipo_de_operacion == "ventaf":
        while ichimoku_1m["Senkou span A"].iloc[-1] < ichimoku_1m["Senkou span B"].iloc[-1]:
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            try:
                ohlc_5s = pd.read_csv("datos_5s.csv", index_col="time")
            except:
                print("reintentando lectura ohlc_5s")
            if sop_min_5m < ohlc_5s['c'].iloc[-1] < sop_max_5m:
                print("Se encuentra en soporte")
                time.sleep(300)
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_5s = ichimoku(ohlc_5s)
                if (ichi_5s["Senkou span B"].iloc[-26] > ohlc_5s["c"].iloc[-1] < ichi_5s["Senkou span A"].iloc[-26]) and \
                        (ichi_5s["tenkan-sen"].iloc[-2] >= ichi_5s["kijun-sen"].iloc[-2] and
                         ichi_5s["tenkan-sen"].iloc[-1] < ichi_5s["kijun-sen"].iloc[-1]):
                    ejecucion("ventaf", par)
                    break
                if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                    ohlc_1m.iloc[-1].name[14:16]) and \
                        (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16])):02}" !=
                         ohlc_1m.iloc[-1].name[14:16]):
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                time.sleep(5 - ((time.time() - starttime) % 5))
        print("se sale del seguimiento porque se ejecutó operacion ó",
              ichimoku_1m["Senkou span A"].iloc[-1] < ichimoku_1m["Senkou span B"].iloc[-1])
