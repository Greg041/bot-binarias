import pandas as pd
import time
import oandapyV20
from ADX import ADX
from macd import MACD
from ExtraccionDatosOanda import ExtraccionOanda
from Ejecucion import ejecucion
from RSI import RSI


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


def seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, tipo_de_divergencia, punto_max_min_macd, punto_ultimo,
                    monto, client):
    print("estamos en seguimiento divergencia")
    if tipo_de_divergencia == "bajista":
        punto_max_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m)
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        while punto_ultimo_macd < punto_max_macd:
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                adx_10s = ADX(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            try:
                print(adx_5m["ADX"].iloc[-1], adx_1m["ADX"].iloc[-1], adx_10s["DI-"].iloc[-1], adx_10s["DI+"].iloc[-1])
                if (adx_1m["ADX"].iloc[-1] < adx_1m["ADX"].iloc[-2]) and (rsi_1m.iloc[-1] < rsi_1m.iloc[-2]):
                    print("posible venta, high 10s: ", ohlc_10s['h'].iloc[-1], " resistencia menor 10s: ", res_min_10s)
                    if ohlc_10s['h'].iloc[-1] >= res_min_10s or ohlc_10s['h'].iloc[-2] >= res_min_10s:
                        while ohlc_10s['c'].iloc[-1] > res_min_10s:
                            try:
                                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s,
                                                                                                            30)
                                time.sleep(10)
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                print("reintentando lectura ohlc_10s")
                                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                        if adx_10s["DI-"].iloc[-1] > adx_10s["DI-"].iloc[-2]:
                            ejecucion("ventac", par, '4', monto)
                            fichero_div = open("datos divergencias.txt", "at")
                            fichero_div.write(f"precio anterior: {ohlc_1m.iloc[-2]} \n"
                                              f"precio actual: {ohlc_1m.iloc[-1]} \n"
                                              f"adx 5m: {adx_5m['ADX'].iloc[-2]} {adx_5m['ADX'].iloc[-1]} \n"
                                              f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                              f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                              f"rsi 5m: {rsi_5m.iloc[-2]} {rsi_5m.iloc[-1]} \n"
                                              f"adx 1m {adx_1m['ADX'].iloc[-2]} {adx_1m['ADX'].iloc[-1]} \n"
                                              f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                              f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                              f"rsi 1m {rsi_1m.iloc[-2]} {rsi_1m.iloc[-1]} \n"
                                              "venta \n")
                            fichero_div.close()
                            time.sleep(120)
                            break
                else:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                            ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                            adx_1m = ADX(ohlc_1m)
                            rsi_1m = RSI(ohlc_1m)
                            punto_ultimo_macd = MACD(ohlc_1m)["MACD"].iloc[-1]
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (ohlc_5m.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                            ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                            adx_5m = ADX(ohlc_5m)
                            rsi_5m = RSI(ohlc_5m)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                    except Exception as e:
                        print(f"excepcion {e}: {type(e)}")
                        print("reintentando lectura ohlc_10s")
                time.sleep(10 - ((time.time() - starttime) % 10))
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                time.sleep(10 - ((time.time() - starttime) % 10))
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd < punto_max_macd, punto_ultimo_macd, punto_max_macd)
    elif tipo_de_divergencia == "alcista":
        punto_min_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m)
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        while punto_ultimo_macd > punto_min_macd:
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                adx_10s = ADX(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            try:
                print(adx_1m["ADX"].iloc[-1], adx_10s["DI+"].iloc[-1], adx_10s["DI-"].iloc[-1])
                if (adx_1m["ADX"].iloc[-1] < adx_1m["ADX"].iloc[-2]) and (rsi_1m.iloc[-1] > rsi_1m.iloc[-2]):
                    print("posible compra, low 10s: ", ohlc_10s['l'].iloc[-1], " soporte max 10s: ", sop_max_10s)
                    if ohlc_10s['l'].iloc[-1] <= sop_max_10s or ohlc_10s['l'].iloc[-2] <= sop_max_10s:
                        while ohlc_10s['c'].iloc[-1] < sop_max_10s:
                            try:
                                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s,
                                                                                                            30)
                                time.sleep(10)
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                print("reintentando lectura ohlc_10s")
                                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                        if adx_10s["DI+"].iloc[-1] > adx_10s["DI+"].iloc[-2]:
                            ejecucion("comprac", par, '4', monto)
                            fichero_div = open("datos divergencias.txt", "at")
                            fichero_div.write(f"precio anterior: {ohlc_1m.iloc[-2]} \n"
                                              f"precio actual: {ohlc_1m.iloc[-1]} \n"
                                              f"adx 5m: {adx_5m['ADX'].iloc[-2]} {adx_5m['ADX'].iloc[-1]} \n"
                                              f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                              f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                              f"rsi 5m: {rsi_5m.iloc[-2]} {rsi_5m.iloc[-1]} \n"
                                              f"adx 1m {adx_1m['ADX'].iloc[-2]} {adx_1m['ADX'].iloc[-1]} \n"
                                              f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                              f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                              f"rsi 1m {rsi_1m.iloc[-2]} {rsi_1m.iloc[-1]} \n"
                                              "compra \n")
                            fichero_div.close()
                            time.sleep(120)
                            break
                else:
                    if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                            ohlc_1m.iloc[-1].name[14:16]):
                        try:
                            ExtraccionOanda(client, 500, 'M1', par)
                            ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                            adx_1m = ADX(ohlc_1m)
                            rsi_1m = RSI(ohlc_1m)
                            punto_ultimo_macd = MACD(ohlc_1m)["MACD"].iloc[-1]
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                    if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                            int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                            (ohlc_5m.iloc[-1].name[
                             14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                        try:
                            ExtraccionOanda(client, 500, 'M5', par)
                            ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                            adx_5m = ADX(ohlc_5m)
                            rsi_5m = RSI(ohlc_5m)
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            client = oandapyV20.API(
                                access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                environment="practice")
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                    except Exception as e:
                        print(f"excepcion {e}: {type(e)}")
                        print("reintentando lectura ohlc_10s")
                time.sleep(10 - ((time.time() - starttime) % 10))
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                time.sleep(10 - ((time.time() - starttime) % 10))
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd > punto_min_macd, punto_ultimo_macd, punto_min_macd)
