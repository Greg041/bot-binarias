import pandas as pd
import time
import oandapyV20
from ADX import ADX
from ExtraccionDatosOanda import ExtraccionOanda
from Ejecucion import ejecucion
from RSI import RSI
from cambiar_monto import cambio_de_monto
from ichimoku import ichimoku


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


def seguimiento_boll(ohlc_5m, ohlc_1m, ohlc_10s, res_max_1min, res_min_1min, res_max_5min, res_min_5min, res_max_30m,
                     res_min_30m, sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, sop_min_30m, sop_max_30m,
                     bollinger_1m, tipo_de_operacion, par, monto, client, request, contador):
    print("seguimiento bollinger")
    tiempo_de_operacion = "6"
    if tipo_de_operacion == "ventac":
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m, periodo=7)
        ichimoku_10s = ichimoku(ohlc_10s)
        tiempo_limite = time.time() + 600
        while (adx_1m["ADX"].iloc[-1] < 32.0) and (rsi_1m.iloc[-1] < 70) and \
                (ohlc_10s['c'].iloc[-1] > bollinger_1m["BB_dn"].iloc[-1]) and time.time() < tiempo_limite:
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
            except:
                pass
            starttime = time.time()
            adx_10s = ADX(ohlc_10s)
            print("posible venta")
            print(f"precio: {ohlc_10s['c'].iloc[-1]}\n", f"tenkan-sen: {ichimoku_10s['tenkan-sen'].iloc[-1]}\n",
                  f"kijun-sen: {ichimoku_10s['kijun-sen'].iloc[-1]}")
            if (ichimoku_10s["tenkan-sen"].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] > ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1] > ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2] > ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["tenkan-sen"].iloc[-1]) and \
                    (adx_10s["ADX"].iloc[-2] > adx_10s["ADX"].iloc[-1]):
                if contador.return_estrategia("venta", "estrategia4"):
                    ejecucion("ventac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"sobre resistencia 1m: {res_max_1min <= ohlc_10s['c'].iloc[-1]} \n"
                                            f"sobre resistencia 5m: {res_max_5min <= ohlc_10s['c'].iloc[-1]} \n"
                                            f"venta \n")
                    if precio >= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("venta")
                        return
                    elif precio < precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            else:
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
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m, periodo=7)
                        res_max_1m, res_min_1min, sop_min_1m, sop_max_1min = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
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
                        res_max_5min, res_min_5min, sop_min_5min, sop_max_5min = \
                            calcular_rango_sop_res(ohlc_5m, 50)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))
    elif tipo_de_operacion == "comprac":
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m, periodo=7)
        ichimoku_10s = ichimoku(ohlc_10s)
        tiempo_limite = time.time() + 600
        while (adx_1m["ADX"].iloc[-1] < 32.0) and (rsi_1m.iloc[-1] < 70) and \
                (ohlc_10s['c'].iloc[-1] < bollinger_1m["BB_up"].iloc[-1]) and time.time() < tiempo_limite:
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
            except:
                pass
            starttime = time.time()
            adx_10s = ADX(ohlc_10s)
            print("posible compra")
            print(f"precio: {ohlc_10s['c'].iloc[-1]}\n", f"tenkan-sen: {ichimoku_10s['tenkan-sen'].iloc[-1]}\n",
                  f"kijun-sen: {ichimoku_10s['kijun-sen'].iloc[-1]}")
            if (ichimoku_10s["tenkan-sen"].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] < ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1] < ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2] < ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["tenkan-sen"].iloc[-1]) and \
                    (adx_10s["ADX"].iloc[-2] > adx_10s["ADX"].iloc[-1]):
                if contador.return_estrategia("compra", "estrategia4"):
                    ejecucion("comprac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"debajo soporte 1m: {ohlc_10s['c'].iloc[-1] <= sop_min_1min} \n"
                                            f"debajo soporte 5m: {ohlc_10s['c'].iloc[-1] <= sop_min_5min} \n"
                                            f"compra \n")
                    if precio <= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("compra")
                        return
                    elif precio > precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            else:
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
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m, periodo=7)
                        res_max_1m, res_min_1min, sop_min_1m, sop_max_1min = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
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
                        res_max_5min, res_min_5min, sop_min_5min, sop_max_5min = \
                            calcular_rango_sop_res(ohlc_5m, 50)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))


def seguimiento_boll5(ohlc_5m, ohlc_1m, ohlc_10s, res_max_1min, res_min_1min, res_max_5min, res_min_5min, res_max_30m,
                     res_min_30m, sop_min_1min, sop_max_1min, sop_min_5min, sop_max_5min, sop_min_30m, sop_max_30m,
                     bollinger_5m, tipo_de_operacion, par, monto, client, request, contador):
    print("seguimiento bollinger 5m")
    tiempo_de_operacion = "6"
    if tipo_de_operacion == "ventac":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m, periodo=7)
        ichimoku_10s = ichimoku(ohlc_10s)
        tiempo_limite = time.time() + 600
        while (adx_5m["ADX"].iloc[-1] < 32.0) and (rsi_5m.iloc[-1] < 70) and \
                (ohlc_10s['c'].iloc[-1] > bollinger_5m["BB_dn"].iloc[-1]) and time.time() < tiempo_limite:
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
            except:
                pass
            starttime = time.time()
            adx_10s = ADX(ohlc_10s)
            print("posible venta")
            print(f"precio: {ohlc_10s['c'].iloc[-1]}\n", f"tenkan-sen: {ichimoku_10s['tenkan-sen'].iloc[-1]}\n",
                  f"kijun-sen: {ichimoku_10s['kijun-sen'].iloc[-1]}")
            if (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] > ichimoku_10s["Senkou span B"].iloc[-26] and
                    ichimoku_10s["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1] > ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2] > ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["tenkan-sen"].iloc[-1]):
                if contador.return_estrategia("venta", "estrategia5"):
                    ejecucion("ventac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"sobre resistencia 1m: {res_max_1min <= ohlc_10s['c'].iloc[-1]} \n"
                                            f"sobre resistencia 5m: {res_max_5min <= ohlc_10s['c'].iloc[-1]} \n"
                                            f"precio encima de la nube 10s\n"
                                            f"venta \n")
                    if precio >= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("venta")
                        return
                    elif precio < precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            elif (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] > ichimoku_10s["Senkou span B"].iloc[-26] and
                    ichimoku_10s["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] < ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1] > ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2] > ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["tenkan-sen"].iloc[-1]):
                if contador.return_estrategia("venta", "estrategia5"):
                    ejecucion("ventac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"sobre resistencia 1m: {res_max_1min <= ohlc_10s['c'].iloc[-1]} \n"
                                            f"sobre resistencia 5m: {res_max_5min <= ohlc_10s['c'].iloc[-1]} \n"
                                            "precio debajo de la nube 10s\n"
                                            f"venta \n")
                    if precio >= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("venta")
                        return
                    elif precio < precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            else:
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
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        res_max_1m, res_min_1min, sop_min_1m, sop_max_1min = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
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
                        res_max_5min, res_min_5min, sop_min_5min, sop_max_5min = \
                            calcular_rango_sop_res(ohlc_5m, 50)
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m, periodo=7)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))
    elif tipo_de_operacion == "comprac":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m, periodo=7)
        ichimoku_10s = ichimoku(ohlc_10s)
        tiempo_limite = time.time() + 600
        while (adx_5m["ADX"].iloc[-1] < 32.0) and (rsi_5m.iloc[-1] < 70) and \
                (ohlc_10s['c'].iloc[-1] < bollinger_5m["BB_up"].iloc[-1]) and time.time() < tiempo_limite:
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
            except:
                pass
            starttime = time.time()
            adx_10s = ADX(ohlc_10s)
            print("posible compra")
            print(f"precio: {ohlc_10s['c'].iloc[-1]}\n", f"tenkan-sen: {ichimoku_10s['tenkan-sen'].iloc[-1]}\n",
                  f"kijun-sen: {ichimoku_10s['kijun-sen'].iloc[-1]}")
            if (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] < ichimoku_10s["Senkou span B"].iloc[-26] and
                    ichimoku_10s["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] < ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1] < ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2] < ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["tenkan-sen"].iloc[-1]):
                if contador.return_estrategia("compra", "estrategia5"):
                    ejecucion("comprac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"debajo soporte 1m: {ohlc_10s['c'].iloc[-1] <= sop_min_1min} \n"
                                            f"debajo soporte 5m: {ohlc_10s['c'].iloc[-1] <= sop_min_5min} \n"
                                            "precio debajo de la nube 10s\n"
                                            f"compra \n")
                    if precio <= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("compra")
                        return
                    elif precio > precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            elif (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2]) and \
                    (ichimoku_10s["Senkou span A"].iloc[-26] < ichimoku_10s["Senkou span B"].iloc[-26] and
                    ichimoku_10s["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] < ichimoku_10s["Senkou span B"].iloc[-26]) and \
                    (ohlc_10s['o'].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1] < ohlc_10s['c'].iloc[-1] or
                     ohlc_10s['o'].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2] < ohlc_10s['c'].iloc[-2]) and \
                    (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["tenkan-sen"].iloc[-1]):
                if contador.return_estrategia("compra", "estrategia5"):
                    ejecucion("comprac", par, tiempo_de_operacion, monto)
                    live_price_data = client.request(request)
                    precio = (float(live_price_data["prices"][0]["closeoutBid"])
                              + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    time.sleep(int(tiempo_de_operacion) * 60)
                    live_price_data = client.request(request)
                    precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                               + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                    ichi_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    rsi_5m = RSI(ohlc_5m)
                    adx_5m = ADX(ohlc_5m)
                    with open("datos estrategia 4.txt", "at") as fichero_est_4:
                        fichero_est_4.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichi_1m['Senkou span A'].iloc[-2]}, {ichi_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichi_1m['Senkou span B'].iloc[-2]}, {ichi_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichi_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichi_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichi_1m['tenkan-sen'].iloc[-2]}, {ichi_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichi_1m['kijun-sen'].iloc[-2]}, {ichi_1m['kijun-sen'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
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
                                            f"debajo soporte 1m: {ohlc_10s['c'].iloc[-1] <= sop_min_1min} \n"
                                            f"debajo soporte 5m: {ohlc_10s['c'].iloc[-1] <= sop_min_5min} \n"
                                            "precio encima de la nube 10s\n"
                                            f"compra \n")
                    if precio <= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("compra")
                        return
                    elif precio > precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            else:
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
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        res_max_1m, res_min_1min, sop_min_1m, sop_max_1min = calcular_rango_sop_res(ohlc_1m, 120)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m1 seguimiento ichimoku")
                try:
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
                        res_max_5min, res_min_5min, sop_min_5min, sop_max_5min = \
                            calcular_rango_sop_res(ohlc_5m, 50)
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m, periodo=7)
                except Exception as e:
                    print(f"excepcion {e}: {type(e)}")
                    print("error en lectura de datos m5 seguimiento ichimoku")
                time.sleep(10 - ((time.time() - starttime) % 10))