import pandas as pd
import time
import oandapyV20
from ADX import ADX
from macd import MACD
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


def seguimiento_div(ohlc_5m, ohlc_1m, ohlc_10s, par, tipo_de_divergencia, punto_max_min_macd, punto_ultimo,
                    monto, client, request):
    print("estamos en seguimiento divergencia")
    tiempo_de_operacion = "5"
    if tipo_de_divergencia == "bajista":
        punto_max_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m)
        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        tiempo_limite = time.time() + 600
        while punto_ultimo_macd < punto_max_macd and time.time() < tiempo_limite:
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                adx_10s = ADX(ohlc_10s)
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            try:
                print(adx_1m["ADX"].iloc[-1])
                print("posible venta, high 10s: ", ohlc_10s['h'].iloc[-1], " resistencia menor 10s: ", res_min_10s)
                if (ohlc_10s['h'].iloc[-1] <= res_min_10s or ohlc_10s['h'].iloc[-2] <= res_min_10s) or \
                        (ohlc_10s['h'].iloc[-1] <= res_min_1m):
                    while ohlc_10s['c'].iloc[-1] > ichimoku_10s['kijun-sen'].iloc[-1] and punto_ultimo_macd < punto_max_macd:
                        try:
                            ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                            ichimoku_10s = ichimoku(ohlc_10s)
                            res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                            print(ohlc_10s['c'].iloc[-1], "kijun sen: ", ichimoku_10s['kijun-sen'].iloc[-1])
                            time.sleep(10)
                            if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                                    int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[
                                        15:16])) == 6) and \
                                    (ohlc_5m.iloc[-1].name[
                                     14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                                try:
                                    ExtraccionOanda(client, 500, 'M5', par)
                                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                                    punto_ultimo_macd = MACD(ohlc_5m)["MACD"].iloc[-1]
                                except Exception as e:
                                    print(f"excepcion {e}: {type(e)}")
                                    client = oandapyV20.API(
                                        access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                        environment="practice")
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            print("reintentando lectura ohlc_10s")
                            ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                            ichimoku_10s = ichimoku(ohlc_10s)
                            res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                    if (ichimoku_10s["tenkan-sen"].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1]) and \
                            (ichimoku_10s["Senkou span A"].iloc[-26] > ichimoku_10s["Senkou span B"].iloc[-26]) and \
                            (ohlc_10s['o'].iloc[-1] > ichimoku_10s["kijun-sen"].iloc[-1] > ohlc_10s['c'].iloc[-1] or
                             ohlc_10s['o'].iloc[-2] > ichimoku_10s["kijun-sen"].iloc[-2] > ohlc_10s['c'].iloc[-2]) and \
                            (ichimoku_10s["tenkan-sen"].iloc[-2] > ichimoku_10s["tenkan-sen"].iloc[-1]) and \
                            (adx_10s["ADX"].iloc[-2] > adx_10s["ADX"].iloc[-1]):
                        ejecucion("ventac", par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
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
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        adx_10s = ADX(ohlc_10s)
                        rsi_10s = RSI(ohlc_10s)
                        with open("datos divergencias.txt", "at") as fichero_div:
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
                                              f"adx 10s {adx_10s['ADX'].iloc[-2]} {adx_10s['ADX'].iloc[-1]} \n"
                                              f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                              f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                              f"rsi 10s: {rsi_10s.iloc[-2]} {rsi_10s.iloc[-1]} \n"
                                              "venta \n")
                        if precio >= precio2:
                            print("operacion ganada, disminyendo martingala")
                            cambio_de_monto(monto, "disminuir")
                            return
                        elif precio < precio2:
                            print("operacion perdida, aumentando martingala")
                            cambio_de_monto(monto, "aumentar")
                            tiempo_limite = time.time() + 600
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                time.sleep(10 - ((time.time() - starttime) % 10))
            if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                    ohlc_1m.iloc[-1].name[14:16]):
                try:
                    ExtraccionOanda(client, 500, 'M1', par)
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    punto_ultimo_macd = MACD(ohlc_1m)["MACD"].iloc[-1]
                    res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
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
                        environment="practice"
                    )
            time.sleep(10 - ((time.time() - starttime) % 10))
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd < punto_max_macd, punto_ultimo_macd, punto_max_macd)
    elif tipo_de_divergencia == "alcista":
        punto_min_macd = punto_max_min_macd
        punto_ultimo_macd = punto_ultimo
        adx_1m = ADX(ohlc_1m)
        rsi_1m = RSI(ohlc_1m)
        res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
        adx_5m = ADX(ohlc_5m)
        rsi_5m = RSI(ohlc_5m)
        tiempo_limite = time.time() + 600
        while punto_ultimo_macd > punto_min_macd and time.time() < tiempo_limite:
            starttime = time.time()
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                adx_10s = ADX(ohlc_10s)
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            try:
                print(adx_1m["ADX"].iloc[-1])
                print("posible compra, low 10s: ", ohlc_10s['l'].iloc[-1], " soporte max 10s: ", sop_max_10s)
                if (ohlc_10s['l'].iloc[-1] <= sop_max_10s or ohlc_10s['l'].iloc[-2] <= sop_max_10s) or \
                        (ohlc_1m['l'].iloc[-1] <= sop_max_1m):
                    while ichimoku_10s["kijun-sen"].iloc[-1] > ohlc_10s['c'].iloc[-1] and punto_ultimo_macd > punto_min_macd:
                        try:
                            ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                            ichimoku_10s = ichimoku(ohlc_10s)
                            res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                            print(ohlc_10s['c'].iloc[-1], "kijun sen: ", ichimoku_10s['kijun-sen'].iloc[-1])
                            time.sleep(10)
                            if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                                    int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[
                                        15:16])) == 6) and \
                                    (ohlc_5m.iloc[-1].name[
                                     14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                                try:
                                    ExtraccionOanda(client, 500, 'M5', par)
                                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                                    punto_ultimo_macd = MACD(ohlc_5m)["MACD"].iloc[-1]
                                except Exception as e:
                                    print(f"excepcion {e}: {type(e)}")
                                    client = oandapyV20.API(
                                        access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                        environment="practice")
                        except Exception as e:
                            print(f"excepcion {e}: {type(e)}")
                            print("reintentando lectura ohlc_10s")
                            ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                            ichimoku_10s = ichimoku(ohlc_10s)
                            res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
                    if (ichimoku_10s["tenkan-sen"].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1]) and \
                            (ichimoku_10s["Senkou span A"].iloc[-26] < ichimoku_10s["Senkou span B"].iloc[-26]) and \
                            (ohlc_10s['o'].iloc[-1] < ichimoku_10s["kijun-sen"].iloc[-1] < ohlc_10s['c'].iloc[-1] or
                             ohlc_10s['o'].iloc[-2] < ichimoku_10s["kijun-sen"].iloc[-2] < ohlc_10s['c'].iloc[
                                 -2]) and \
                            (ichimoku_10s["tenkan-sen"].iloc[-2] < ichimoku_10s["tenkan-sen"].iloc[-1]) and \
                            (adx_10s["ADX"].iloc[-2] > adx_10s["ADX"].iloc[-1]):
                        ejecucion("comprac", par, tiempo_de_operacion, monto)
                        live_price_data = client.request(request)
                        precio = (float(live_price_data["prices"][0]["closeoutBid"])
                                  + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                                ohlc_1m.iloc[-1].name[14:16]):
                            try:
                                ExtraccionOanda(client, 500, 'M1', par)
                                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                                adx_1m = ADX(ohlc_1m)
                                rsi_1m = RSI(ohlc_1m)
                            except Exception as e:
                                print(f"excepcion {e}: {type(e)}")
                                client = oandapyV20.API(
                                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                    environment="practice")
                        time.sleep(int(tiempo_de_operacion) * 60)
                        live_price_data = client.request(request)
                        precio2 = (float(live_price_data["prices"][0]["closeoutBid"])
                                   + float(live_price_data["prices"][0]["closeoutAsk"])) / 2
                        adx_10s = ADX(ohlc_10s)
                        rsi_10s = RSI(ohlc_10s)
                        with open("datos divergencias.txt", "at") as fichero_div:
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
                                              f"adx 10s {adx_10s['ADX'].iloc[-2]} {adx_10s['ADX'].iloc[-1]} \n"
                                              f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                              f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                              f"rsi 10s: {rsi_10s.iloc[-2]} {rsi_10s.iloc[-1]} \n"
                                              "compra \n")
                        if precio <= precio2:
                            print("operacion ganada, disminyendo martingala")
                            cambio_de_monto(monto, "disminuir")
                            return
                        elif precio > precio2:
                            print("operacion perdida, aumentando martingala")
                            cambio_de_monto(monto, "aumentar")
                            tiempo_limite = time.time() + 600
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                time.sleep(10 - ((time.time() - starttime) % 10))
            if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                    ohlc_1m.iloc[-1].name[14:16]):
                try:
                    ExtraccionOanda(client, 500, 'M1', par)
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    punto_ultimo_macd = MACD(ohlc_1m)["MACD"].iloc[-1]
                    res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
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
                        environment="practice"
                    )
            time.sleep(10 - ((time.time() - starttime) % 10))
        print("Se sale del seguimiento porque se ejecuto o",
              punto_ultimo_macd > punto_min_macd, punto_ultimo_macd, punto_min_macd)
