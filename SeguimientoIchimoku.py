from ichimoku import ichimoku
from Ejecucion import ejecucion
from ADX import ADX
from RSI import RSI
from ExtraccionDatosOanda import ExtraccionOanda
import oandapyV20
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


def seguimiento_ichimoku(ohlc_10s, ohlc_1m, datos_5min, ichimoku_1m, par, tipo_de_operacion, res_max_5m, res_min_5m,
                         sop_min_5m,
                         sop_max_5m,
                         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m, monto, client):
    print("estamos en seguimiento")
    if tipo_de_operacion == "compraf":
        while ichimoku_1m["Senkou span A"].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[-1]:
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
            if res_max_5m > ohlc_10s['c'].iloc[-1] > res_min_5m:
                break
            if res_max_1m > ohlc_10s['c'].iloc[-1] > res_min_1m:
                print("Se encuentra en resistencia")
                time.sleep(60)
                try:
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura datos m1 seguimiento ichimoku")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_10s = ichimoku(ohlc_10s)
                if (ichi_10s["Senkou span A"].iloc[-26] < ohlc_10s["c"].iloc[-1] > ichi_10s["Senkou span B"].iloc[
                    -26]) and \
                        (ichi_10s["tenkan-sen"].iloc[-2] <= ichi_10s["kijun-sen"].iloc[-2] and
                         ichi_10s["tenkan-sen"].iloc[-1] > ichi_10s["kijun-sen"].iloc[-1]):
                    ejecucion(tipo_de_operacion, par, '10', monto)
                    break
                # Se verifica que el dataframe esté actualizado tomando en cuenta el minuto actual y el ultimo
                # minuto del dataframe para actualizar los valores del ichimoku
                try:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (datos_5min.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
                        res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(datos_5min, 50)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))
        if res_max_5m > ohlc_10s['c'].iloc[-1] > res_min_5m:
            print("se sale de seguimiento porque hay una resistencia muy fuerte cernaca")
        else:
            print("se sale del seguimiento porque se ejecutó operacion ó",
                  ichimoku_1m["Senkou span A"].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[-1])
    elif tipo_de_operacion == "ventaf":
        while ichimoku_1m["Senkou span A"].iloc[-1] < ichimoku_1m["Senkou span B"].iloc[-1]:
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                print("reintentando lectura ohlc_10s")
            if sop_min_5m < ohlc_10s['c'].iloc[-1] < sop_max_5m:
                break
            if sop_min_1m < ohlc_10s['c'].iloc[-1] < sop_max_1m:
                print("Se encuentra en soporte")
                time.sleep(60)
                try:
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura datos m1 seguimiento ichimoku")
                ichimoku_1m = ichimoku(ohlc_1m)
            else:
                ichi_10s = ichimoku(ohlc_10s)
                if (ichi_10s["Senkou span B"].iloc[-26] > ohlc_10s["c"].iloc[-1] < ichi_10s["Senkou span A"].iloc[
                    -26]) and \
                        (ichi_10s["tenkan-sen"].iloc[-2] >= ichi_10s["kijun-sen"].iloc[-2] and
                         ichi_10s["tenkan-sen"].iloc[-1] < ichi_10s["kijun-sen"].iloc[-1]):
                    ejecucion(tipo_de_operacion, par, '10', monto)
                    break
                # Se verifica que el dataframe esté actualizado tomando en cuenta el minuto actual y el ultimo
                # minuto del dataframe para actualizar los valores del ichimoku
                try:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (datos_5min.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
                        res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(datos_5min, 50)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))
        if sop_min_5m < ohlc_10s['c'].iloc[-1] < sop_max_5m:
            print("Se sale del seguimiento porque hay un soporte fuerte cercano")
        else:
            print("se sale del seguimiento porque se ejecutó operacion ó",
                  ichimoku_1m["Senkou span A"].iloc[-1] < ichimoku_1m["Senkou span B"].iloc[-1])


def seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, tipo_de_operacion, res_max_30m, res_min_30m, sop_min_30m,
                          sop_max_30m, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m, res_max_1m, res_min_1m,
                          sop_min_1m, sop_max_1m, monto, client):
    print("estamos en seguimiento")
    if tipo_de_operacion == "compraf":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        ichimoku_1m = ichimoku(ohlc_1m)
        while (adx_5m["ADX"].iloc[-1] > 20.0) and (rsi_5m.iloc[-1] < 70.0) and \
                (ichimoku_1m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[
                    -26]):
            # Si choca contra una resistencia sale del seguimiento
            if res_max_5m > ohlc_10s['c'].iloc[-1] > res_min_5m or res_max_1m > ohlc_10s['c'].iloc[-1] > res_min_1m or \
                    res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m:
                break
            starttime = time.time()
            ichimoku_10s = ichimoku(ohlc_10s)
            print(ichimoku_10s["tenkan-sen"].iloc[-1], ichimoku_10s["kijun-sen"].iloc[-1])
            if ichimoku_10s["tenkan-sen"].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1]:
                ejecucion(tipo_de_operacion, par, '10', monto)
                fichero_est_3 = open("datos estrategia 3.txt", "at")
                fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                    f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                    f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                    f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                    f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                    f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-1]} \n")
                fichero_est_3.close()
                time.sleep(120)
                break
            else:
                try:
                    ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 120)
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (ohlc_5m.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(ohlc_5m, 50)
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("hubo un error en la lectura de datos 1m o 5m en seguimiento ichimoku 2")
                time.sleep(10 - ((time.time() - starttime) % 10))
        if res_max_5m > ohlc_10s['c'].iloc[-1] > res_min_5m or res_max_1m > ohlc_10s['c'].iloc[-1] > res_min_1m or \
                    res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m:
            print("se sale del seguimiento porque hay una resistencia cercana")
        else:
            print("se sale del seguimiento porque se ejecutó operacion o",
                  adx_5m["ADX"].iloc[-1] > 20.0, rsi_5m.iloc[-1] < 70.0,
                  ichimoku_1m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] >
                  ichimoku_1m["Senkou span B"].iloc[-26])
    elif tipo_de_operacion == "ventaf":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        ichimoku_1m = ichimoku(ohlc_1m)
        while (adx_5m["ADX"].iloc[-1] > 20.0) \
                and (rsi_5m.iloc[-1] > 30.0) and (ichimoku_1m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                                                  ichimoku_1m["Senkou span B"].iloc[-26]):
            if sop_max_5m > ohlc_10s['c'].iloc[-1] > sop_min_5m or sop_max_1m > ohlc_10s['c'].iloc[-1] > sop_min_1m or\
                    sop_max_30m > ohlc_10s['c'].iloc[-1] > sop_min_30m:
                break
            starttime = time.time()
            ichimoku_10s = ichimoku(ohlc_10s)
            print(ichimoku_10s["tenkan-sen"].iloc[-1], ichimoku_10s["kijun-sen"].iloc[-1])
            if ichimoku_10s["tenkan-sen"].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1]:
                ejecucion(tipo_de_operacion, par, '10', monto)
                fichero_est_3 = open("datos estrategia 3.txt", "at")
                fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                    f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                    f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                    f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                    f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                    f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-1]} \n")
                fichero_est_3.close()
                time.sleep(120)
                break
            else:
                try:
                    ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 120)
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (ohlc_5m.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(ohlc_5m, 50)
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("hubo un error en la lectura de datos 1m o 5m en seguimiento ichimoku 2")
                time.sleep(10 - ((time.time() - starttime) % 10))
        if sop_max_5m > ohlc_10s['c'].iloc[-1] > sop_min_5m or sop_max_1m > ohlc_10s['c'].iloc[-1] > sop_min_1m or\
                    sop_max_30m > ohlc_10s['c'].iloc[-1] > sop_min_30m:
            print("Se sale del seguimiento porque hay un soporte cercano")
        else:
            print("se sale del seguimiento porque se ejecutó operacion o ",
                  adx_5m["ADX"].iloc[-1] > 20.0, rsi_5m.iloc[-1] > 30.0,
                  ichimoku_1m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                  ichimoku_1m["Senkou span B"].iloc[-26])
