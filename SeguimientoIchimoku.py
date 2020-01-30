from ichimoku import ichimoku
from Ejecucion import ejecucion
import pandas as pd
import time


def calcular_rango_sop_res(ohlc, rango_velas):
    resistencia_mayor = ohlc["h"].rolling(rango_velas).max().dropna()
    resistencia_menor = ohlc["c"].rolling(rango_velas).max().dropna()
    soporte_menor = ohlc["l"].rolling(rango_velas).min().dropna()
    soporte_mayor = ohlc["c"].rolling(rango_velas).min().dropna()
    resistencia_punto_mayor = resistencia_mayor.iloc[-1]
    resistencia_punto_menor = resistencia_menor.iloc[-1]
    for data in range(-rango_velas, 0):
        precio_h = ohlc['h'].iloc[data]
        precio_o = ohlc['o'].iloc[data]
        precio_c = ohlc['c'].iloc[data]
        if precio_h > resistencia_punto_menor > precio_c:
            if precio_c >= precio_o:
                resistencia_punto_menor = precio_c
            elif precio_c < precio_o < resistencia_punto_menor:
                resistencia_punto_menor = precio_o
    soporte_punto_menor = soporte_menor.iloc[-1]
    soporte_punto_mayor = soporte_mayor.iloc[-1]
    for data in range(-rango_velas, 0):
        precio_l = ohlc['l'].iloc[data]
        precio_o = ohlc['o'].iloc[data]
        precio_c = ohlc['c'].iloc[data]
        if precio_l < soporte_punto_mayor < precio_c:
            if precio_c <= precio_o:
                soporte_punto_mayor = precio_c
            elif precio_c > precio_o > soporte_punto_mayor:
                soporte_punto_mayor = precio_o
    return resistencia_punto_mayor, resistencia_punto_menor, soporte_punto_menor, soporte_punto_mayor


def seguimiento_ichimoku(ohlc_1m, ichimoku_1m, par, tipo_de_operacion, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m,
                         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m):
    print("estamos en seguimiento")
    if tipo_de_operacion == "compraf":
        while ichimoku_1m["Senkou span A"].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[-1]:
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            try:
                ohlc_5s = pd.read_csv("datos_5s.csv", index_col="time")
            except:
                print("reintentando lectura ohlc_5s")
            if res_max_5m > ohlc_5s['c'].iloc[-1] > res_min_5m or res_max_1m > ohlc_5s['c'].iloc[-1] > res_min_1m:
                print("Se encuentra en resistencia")
                time.sleep(60)
                try:
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                except:
                    print("error en lectura datos m1 seguimiento ichimoku")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_5s = ichimoku(ohlc_5s)
                if (ichi_5s["Senkou span A"].iloc[-26] < ohlc_5s["c"].iloc[-1] > ichi_5s["Senkou span B"].iloc[-26]) and \
                        (ichi_5s["tenkan-sen"].iloc[-2] <= ichi_5s["kijun-sen"].iloc[-2] and
                         ichi_5s["tenkan-sen"].iloc[-1] > ichi_5s["kijun-sen"].iloc[-1]):
                    ejecucion("compraf", par)
                    break
                # Se verifica que el dataframe esté actualizado tomando en cuenta el minutoa actual y el ultimo
                # minuto del dataframe para actualizar los valores del ichimoku
                try:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                        ohlc_1m.iloc[-1].name[14:16]) and \
                            (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16])):02}" !=
                             ohlc_1m.iloc[-1].name[14:16]):
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 150)
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (datos_5min.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
                        res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(datos_5min, 50)
                except:
                    print("error en lectura datos m1 seguimiento ichimoku")
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
            if sop_min_5m < ohlc_5s['c'].iloc[-1] < sop_max_5m or sop_min_1m < ohlc_5s['c'].iloc[-1] < sop_max_1m:
                print("Se encuentra en soporte")
                time.sleep(60)
                try:
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                except:
                    print("error en lectura datos m1 seguimiento ichimoku")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_5s = ichimoku(ohlc_5s)
                if (ichi_5s["Senkou span B"].iloc[-26] > ohlc_5s["c"].iloc[-1] < ichi_5s["Senkou span A"].iloc[-26]) and \
                        (ichi_5s["tenkan-sen"].iloc[-2] >= ichi_5s["kijun-sen"].iloc[-2] and
                         ichi_5s["tenkan-sen"].iloc[-1] < ichi_5s["kijun-sen"].iloc[-1]):
                    ejecucion("ventaf", par)
                    break
                # Se verifica que el dataframe esté actualizado tomando en cuenta el minutoa actual y el ultimo
                # minuto del dataframe para actualizar los valores del ichimoku
                try:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                        ohlc_1m.iloc[-1].name[14:16]) and \
                            (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16])):02}" !=
                             ohlc_1m.iloc[-1].name[14:16]):
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                except:
                    print("error en lectura de datos m1 seguimiento ichimoku")
                time.sleep(5 - ((time.time() - starttime) % 5))
        print("se sale del seguimiento porque se ejecutó operacion ó",
              ichimoku_1m["Senkou span A"].iloc[-1] < ichimoku_1m["Senkou span B"].iloc[-1])
