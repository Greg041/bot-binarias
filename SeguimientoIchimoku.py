from ichimoku import ichimoku
from Ejecucion import ejecucion
from ADX import ADX
from RSI import RSI
from ExtraccionDatosOanda import ExtraccionOanda
import oandapyV20
import pandas as pd
import time
from cambiar_monto import cambio_de_monto


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


def seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, tipo_de_operacion, res_max_30m, res_min_30m, sop_min_30m,
                          sop_max_30m, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m, res_max_1m, res_min_1m,
                          sop_min_1m, sop_max_1m, monto, client, request, contador):
    print("estamos en seguimiento")
    tiempo_de_operacion = "3"
    if tipo_de_operacion == "compraf":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        ichimoku_1m = ichimoku(ohlc_1m)
        tiempo_limite = time.time() + 600
        while (adx_5m["ADX"].iloc[-1] > 20.0) and (rsi_5m.iloc[-1] > 30.0) and \
                (ichimoku_1m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichimoku_1m["Senkou span B"].iloc[
                    -26]) and (time.time() < tiempo_limite):
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                ichimoku_10s = ichimoku(ohlc_10s)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                ichimoku_10s = ichimoku(ohlc_10s)
            print("posible compra, low 10s: ", ohlc_10s['l'].iloc[-1], " soporte max 10s: ", sop_max_10s)
            if (ohlc_10s['l'].iloc[-1] <= sop_max_10s or ohlc_10s['l'].iloc[-2] <= sop_max_10s) or \
                    (ohlc_10s['l'].iloc[-1] <= sop_max_1m):
                while ohlc_10s['c'].iloc[-1] < ichimoku_10s['kijun-sen'].iloc[-1] or \
                        ohlc_10s['c'].iloc[-1] < ichimoku_10s['tenkan-sen'].iloc[-1]:
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ichimoku_10s = ichimoku(ohlc_10s)
                        res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                        time.sleep(10)
                    except Exception as e:
                        print(f"excepcion {e}: {type(e)}")
                        print("reintentando lectura ohlc_10s")
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ichimoku_10s = ichimoku(ohlc_10s)
                        res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                if (ichimoku_10s["Senkou span B"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                    ichimoku_10s["Senkou span A"].iloc[-26] <
                    ichimoku_10s["Senkou span B"].iloc[-26]) \
                        and (ichimoku_10s['tenkan-sen'].iloc[-2] < ichimoku_10s['tenkan-sen'].iloc[-1]) \
                        and (ohlc_10s['o'].iloc[-1] < ichimoku_10s['kijun-sen'].iloc[-1] < ohlc_10s['c'].iloc[-1]):
                    if contador.return_estrategia("compra", "estrategia3") < 2:
                        ejecucion(tipo_de_operacion, par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                                ohlc_1m.iloc[-1].name[14:16]):
                            try:
                                ExtraccionOanda(client, 500, 'M1', par)
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
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                client = oandapyV20.API(
                                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                    environment="practice")
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                        ichi_5m = ichimoku(ohlc_5m)
                        with open("datos estrategia 3.txt", "at") as fichero_est_3:
                            fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                                f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                                f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku tenkan 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}, {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                                f"ichimoku kijun 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                                f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                                f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                                f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
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
                elif (ichimoku_10s["Senkou span B"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichimoku_10s["Senkou span A"].iloc[-26] >
                    ichimoku_10s["Senkou span B"].iloc[-26]) \
                        and (ichimoku_10s['tenkan-sen'].iloc[-2] <= ichimoku_10s['tenkan-sen'].iloc[-1]) \
                        and (ohlc_10s['o'].iloc[-1] < ichimoku_10s['tenkan-sen'].iloc[-1] < ohlc_10s['c'].iloc[-1] or
                             ohlc_10s['o'].iloc[-1] < ichimoku_10s['kijun-sen'].iloc[-1] < ohlc_10s['c'].iloc[-1]):
                    if contador.return_estrategia("compra", "estrategia3") < 2:
                        ejecucion(tipo_de_operacion, par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                                ohlc_1m.iloc[-1].name[14:16]):
                            try:
                                ExtraccionOanda(client, 500, 'M1', par)
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
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                client = oandapyV20.API(
                                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                    environment="practice")
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                        ichi_5m = ichimoku(ohlc_5m)
                        with open("datos estrategia 3.txt", "at") as fichero_est_3:
                            fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                                f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                                f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku tenkan 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}, {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                                f"ichimoku kijun 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                                f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                                f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                                f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
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
                    res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
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
        if res_max_5m > ohlc_10s['c'].iloc[-1] > res_min_5m or res_max_30m > ohlc_10s['c'].iloc[-1] > res_min_30m:
            print("se sale del seguimiento porque hay una resistencia cercana")
        else:
            print("se sale del seguimiento porque se ejecutó operacion o",
                  adx_5m["ADX"].iloc[-1] > 20.0, rsi_5m.iloc[-1] > 30.0,
                  ichimoku_1m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] >
                  ichimoku_1m["Senkou span B"].iloc[-26])
    elif tipo_de_operacion == "ventaf":
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        ichimoku_1m = ichimoku(ohlc_1m)
        tiempo_limite = time.time() + 600
        while (adx_5m["ADX"].iloc[-1] > 20.0) \
                and (rsi_5m.iloc[-1] < 70.0) and (ichimoku_1m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                                                  ichimoku_1m["Senkou span B"].iloc[-26]) and (time.time() < tiempo_limite):
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                ichimoku_10s = ichimoku(ohlc_10s)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                ichimoku_10s = ichimoku(ohlc_10s)
            print("posible venta, high 10s: ", ohlc_10s['h'].iloc[-1], " resistencia menor 10s: ", res_min_10s)
            if (ohlc_10s['h'].iloc[-1] >= res_min_10s or ohlc_10s['h'].iloc[-2] >= res_min_10s) or \
                    (ohlc_10s['h'].iloc[-1] >= res_min_1m):
                while ohlc_10s['c'].iloc[-1] > ichimoku_10s['kijun-sen'].iloc[-1] or \
                        ohlc_10s['c'].iloc[-1] > ichimoku_10s['tenkan-sen'].iloc[-1]:
                    try:
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ichimoku_10s = ichimoku(ohlc_10s)
                        res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                        time.sleep(10)
                    except Exception as e:
                        print(f"excepcion {e}: {type(e)}")
                        print("reintentando lectura ohlc_10s")
                        ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                        ichimoku_10s = ichimoku(ohlc_10s)
                        res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                if (ichimoku_10s["Senkou span B"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichimoku_10s["Senkou span A"].iloc[-26] >
                    ichimoku_10s["Senkou span B"].iloc[-26]) \
                        and (ichimoku_10s['tenkan-sen'].iloc[-2] > ichimoku_10s['tenkan-sen'].iloc[-1]) \
                        and (ohlc_10s['o'].iloc[-1] > ichimoku_10s['kijun-sen'].iloc[-1] > ohlc_10s['c'].iloc[-1]):
                    if contador.return_estrategia("venta", "estrategia3"):
                        ejecucion(tipo_de_operacion, par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                                ohlc_1m.iloc[-1].name[14:16]):
                            try:
                                ExtraccionOanda(client, 500, 'M1', par)
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
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                client = oandapyV20.API(
                                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                    environment="practice")
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                        ichi_5m = ichimoku(ohlc_5m)
                        with open("datos estrategia 3.txt", "at") as fichero_est_3:
                            fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                                f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                                f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku tenkan 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}, {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                                f"ichimoku kijun 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                                f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                                f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                                f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
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
                elif (ichimoku_10s["Senkou span B"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                    ichimoku_10s["Senkou span A"].iloc[-26] < ichimoku_10s["Senkou span B"].iloc[-26]) \
                        and (ichimoku_10s['tenkan-sen'].iloc[-2] >= ichimoku_10s['tenkan-sen'].iloc[-1]) \
                        and (ohlc_10s['o'].iloc[-1] > ichimoku_10s['tenkan-sen'].iloc[-1] > ohlc_10s['c'].iloc[-1] or
                             ohlc_10s['o'].iloc[-1] > ichimoku_10s['kijun-sen'].iloc[-1] > ohlc_10s['c'].iloc[-1]):
                    if contador.return_estrategia("venta", "estrategia3"):
                        ejecucion(tipo_de_operacion, par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
                                ohlc_1m.iloc[-1].name[14:16]):
                            try:
                                ExtraccionOanda(client, 500, 'M1', par)
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
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                client = oandapyV20.API(
                                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                    environment="practice")
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                        ichimoku_1m = ichimoku(ohlc_1m)
                        adx_1m = ADX(ohlc_1m)
                        rsi_1m = RSI(ohlc_1m)
                        ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                        adx_5m = ADX(ohlc_5m)
                        rsi_5m = RSI(ohlc_5m)
                        ichi_5m = ichimoku(ohlc_5m)
                        with open("datos estrategia 3.txt", "at") as fichero_est_3:
                            fichero_est_3.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                                f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                                f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                                f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                                f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                                f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                                f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                                f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                                f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                                f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                                f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku tenkan 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}, {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                                f"ichimoku kijun 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                                f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                                f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                                f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                                f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
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
                    res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
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
        if sop_max_5m > ohlc_10s['c'].iloc[-1] > sop_min_5m or sop_max_30m > ohlc_10s['c'].iloc[-1] > sop_min_30m:
            print("Se sale del seguimiento porque hay un soporte cercano")
        else:
            print("se sale del seguimiento porque se ejecutó operacion o ",
                  adx_5m["ADX"].iloc[-1] > 20.0, rsi_5m.iloc[-1] < 70.0,
                  ichimoku_1m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                  ichimoku_1m["Senkou span B"].iloc[-26])
