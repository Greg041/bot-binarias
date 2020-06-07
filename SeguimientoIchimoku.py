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


def seguimiento_ichimoku(ohlc_10s, ohlc_1m, ohlc_5m, ichimoku_1m, par, tipo_de_operacion, res_max_30m, res_min_30m,
                         sop_min_30m, sop_max_30m, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m,
                         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m, monto, client, request, contador,
                         array_de_precios,
                         array_rangos_validos):
    print("estamos en seguimiento")
    tiempo_de_operacion = "6"
    if tipo_de_operacion == "compraf":
        tiempo_limite = time.time() + 600
        while (ichimoku_1m["tenkan-sen"].iloc[-1] >= ichimoku_1m["kijun-sen"].iloc[-1]) and (
                ichimoku_1m["Senkou span A"].iloc[-2] <= ichimoku_1m["Senkou span A"].iloc[-1]) and (time.time() <
                                                                                                     tiempo_limite):
            print(ichimoku_1m["Senkou span A"].iloc[-1], ichimoku_1m["Senkou span B"].iloc[-1])
            starttime = time.time()
            ichi_5m = ichimoku(ohlc_5m)
            if (ichi_5m["Senkou span A"].iloc[-26] <= ohlc_5m['c'].iloc[-1] <= ichi_5m["Senkou span B"].iloc[-26] or
                ichi_5m["Senkou span B"].iloc[-26] <= ohlc_5m['c'].iloc[-1] <= ichi_5m["Senkou span A"].iloc[-26]) or \
                    (ichi_5m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] < ichi_5m["Senkou span B"].iloc[-26]):
                print("se sale del seguimiento porque el precio volvio a estar lateral")
                print(f"precio: {ohlc_10s['c'].iloc[-1]}, ichi_5m Span A: {ichi_5m['Senkou span A'].iloc[-26]}, "
                      f"ichi_5m Span B: {ichi_5m['Senkou span B'].iloc[-26]}")
                return
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            """
            Indice de valores de los arrays:
                array_de_precios = [ultimo_precio, rango_setenta, rango_treinta]
                array_rangos_validos = [soporte_treinta, resistencia_setenta, soporte_inferior, resistencia_superior]
            """
            print("posible compra: ", array_de_precios[0], "resistencia validada: ",
                  array_rangos_validos[1], "soporte inferior validado: ",
                  array_rangos_validos[2])
            # variación cuando el precio se encuentra en cualquier parte de la parte superior del 70% del
            # rango y el soporte inferior no está validado signigicando un rebote en el precio del rango
            # inferior
            if (not array_rangos_validos[2]) and (not array_rangos_validos[1]):
                # si se ha ejecutado la misma operación 2 veces antes, entonces no ejecutar una 3ra
                if contador.return_estrategia("compra", "estrategia1") < 2:
                    # al ejecutar la operacion se retorna el precio aproximado donde estaba al momento de
                    # ejecutarse, si retorna 0 es porque la operación no se ejecutó porque pasó mucho tiempo
                    precio = ejecucion("compra1", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
                    adx_10s = ADX(ohlc_10s)
                    rsi_10s = RSI(ohlc_10s)
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
                    precio2 = array_de_precios[0]
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                    adx_5m = ADX(ohlc_5m)
                    rsi_5m = RSI(ohlc_5m)
                    ichi_5m = ichimoku(ohlc_5m)
                    with open("datos estrategia 1.txt", "at") as fichero_est_1:
                        fichero_est_1.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichimoku_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichimoku_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}. {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]}\n"
                                            f"ichimoku 5m sspan A: {ichi_5m['Senkou span A'].iloc[-2]}, {ichi_5m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan B: {ichi_5m['Senkou span B'].iloc[-2]}, {ichi_5m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan A -26: {ichi_5m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 5m sspan B -26: {ichi_5m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 5m: {ichi_5m['tenkan-sen'].iloc[-2]}. {ichi_5m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 5m: {ichi_5m['kijun-sen'].iloc[-2]}, {ichi_5m['kijun-sen'].iloc[-1]}\n"
                                            f"rsi 10s: {rsi_10s.iloc[-2]}, {rsi_10s.iloc[-1]} \n"
                                            f"adx 10s: {adx_10s['ADX'].iloc[-2]}, {adx_10s['ADX'].iloc[-1]} \n"
                                            f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                            f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                            f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                            f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                            f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                            f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                            f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n" 
                                            f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                            f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                            "variacion 1 \n"
                                            f"compra \n")
                    print("se sale del seguimiento porque se ejecutó operacion")
                    if precio <= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("compra")
                        return
                    elif precio > precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            # variación cuando el precio se encuentra debajo del rango del 30%
            elif array_de_precios[0] <= array_de_precios[2] and array_rangos_validos[2]:
                if contador.return_estrategia("compra", "estrategia1") < 2:
                    precio = ejecucion("compra2", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
                    adx_10s = ADX(ohlc_10s)
                    rsi_10s = RSI(ohlc_10s)
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
                    precio2 = array_de_precios[0]
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                    adx_5m = ADX(ohlc_5m)
                    rsi_5m = RSI(ohlc_5m)
                    ichi_5m = ichimoku(ohlc_5m)
                    with open("datos estrategia 1.txt", "at") as fichero_est_1:
                        fichero_est_1.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichimoku_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichimoku_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}. {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]}\n"
                                            f"ichimoku 5m sspan A: {ichi_5m['Senkou span A'].iloc[-2]}, {ichi_5m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan B: {ichi_5m['Senkou span B'].iloc[-2]}, {ichi_5m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan A -26: {ichi_5m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 5m sspan B -26: {ichi_5m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 5m: {ichi_5m['tenkan-sen'].iloc[-2]}. {ichi_5m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 5m: {ichi_5m['kijun-sen'].iloc[-2]}, {ichi_5m['kijun-sen'].iloc[-1]}\n"
                                            f"rsi 10s: {rsi_10s.iloc[-2]}, {rsi_10s.iloc[-1]} \n"
                                            f"adx 10s: {adx_10s['ADX'].iloc[-2]}, {adx_10s['ADX'].iloc[-1]} \n"
                                            f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                            f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                            f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                            f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                            f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                            f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                            f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                            f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                            f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                            "variacion 2\n"
                                            f"compra \n")
                    print("se sale del seguimiento porque se ejecutó operacion")
                    if precio <= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("compra")
                        return
                    elif precio > precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            # Se verifica que el dataframe esté actualizado tomando en cuenta el minuto actual y el ultimo
            # minuto del dataframe para actualizar los valores del ichimoku
            # try:
            #     if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
            #             ohlc_1m.iloc[-1].name[14:16]):
            #         try:
            #             ExtraccionOanda(client, 500, 'M1', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
            #         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = \
            #             calcular_rango_sop_res(ohlc_1m, 10)
            #         ichimoku_1m = ichimoku(ohlc_1m)
            # except Exception as e:
            #     print(f"excepcion {e}: {type(e)}")
            #     print("error en lectura de datos m1 seguimiento ichimoku")
            # try:
            #     if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
            #             int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
            #             (ohlc_5m.iloc[-1].name[
            #              14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
            #         try:
            #             ExtraccionOanda(client, 500, 'M5', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
            # except Exception as e:
            #     print(f"excepcion {e}: {type(e)}")
            #     print("error en lectura de datos m5 seguimiento ichimoku")
            time.sleep(1)
        print("Se sale del seguimiento porque se ejecutó operación o ",
              (ichimoku_1m["tenkan-sen"].iloc[-2] <= ichimoku_1m["tenkan-sen"].iloc[-1] and
               ichimoku_1m["tenkan-sen"].iloc[-1] >= ichimoku_1m["kijun-sen"].iloc[-1]) and (
                      ichimoku_1m["Senkou span A"].iloc[-2] <= ichimoku_1m["Senkou span A"].iloc[-1]))
    elif tipo_de_operacion == "ventaf":
        tiempo_limite = time.time() + 600
        while (ichimoku_1m["tenkan-sen"].iloc[-1] <= ichimoku_1m["kijun-sen"].iloc[-1]) and (
                ichimoku_1m["Senkou span A"].iloc[-2] >= ichimoku_1m["Senkou span A"].iloc[-1]) and (time.time() <
                                                                                                     tiempo_limite):
            ichi_5m = ichimoku(ohlc_5m)
            if (ichi_5m["Senkou span A"].iloc[-26] <= ohlc_5m['c'].iloc[-1] <= ichi_5m["Senkou span B"].iloc[-26] or
                ichi_5m["Senkou span B"].iloc[-26] <= ohlc_5m['c'].iloc[-1] <= ichi_5m["Senkou span A"].iloc[-26]) or \
                    (ichi_5m["Senkou span A"].iloc[-26] < ohlc_10s['c'].iloc[-1] > ichi_5m["Senkou span B"].iloc[-26]):
                print("se sale del seguimiento porque el precio volvio a estar lateral")
                print(f"precio: {ohlc_10s['c'].iloc[-1]}, ichi_5m Span A: {ichi_5m['Senkou span A'].iloc[-26]}, "
                      f"ichi_5m Span B: {ichi_5m['Senkou span B'].iloc[-26]}")
                return
            try:
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            except Exception as e:
                print(f"excepcion {e}: {type(e)}")
                print("reintentando lectura ohlc_10s")
                ohlc_10s = pd.read_csv("datos_10s.csv", index_col="time")
                ichimoku_10s = ichimoku(ohlc_10s)
                res_max_10s, res_min_10s, sop_min_10s, sop_max_10s = calcular_rango_sop_res(ohlc_10s, 30)
            """
            Indice de valores de los arrays:
                array_de_precios = [ultimo_precio, rango_setenta, rango_treinta]
                array_rangos_validos = [soporte_treinta, resistencia_setenta, soporte_inferior, resistencia_superior]
            """
            print("posible venta, precio", array_de_precios[0], "soporte valido: ", array_rangos_validos[0],
                  "resistencia superior valida: ", array_rangos_validos[3])
            # variación cuando el precio se encuentra en cualquier parte de la parte inferior 30% del
            # rango y la resistencia superior no está validada signigicando un rebote en el precio del rango
            # superior
            if (not array_rangos_validos[3]) and (not array_rangos_validos[0]):
                if contador.return_estrategia("venta", "estrategia1") < 2:
                    precio = ejecucion("venta1", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
                    adx_10s = ADX(ohlc_10s)
                    rsi_10s = RSI(ohlc_10s)
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
                    precio2 = array_de_precios[0]
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                    adx_5m = ADX(ohlc_5m)
                    rsi_5m = RSI(ohlc_5m)
                    ichi_5m = ichimoku(ohlc_5m)
                    with open("datos estrategia 1.txt", "at") as fichero_est_1:
                        fichero_est_1.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichimoku_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichimoku_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}. {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]}\n"
                                            f"ichimoku 5m sspan A: {ichi_5m['Senkou span A'].iloc[-2]}, {ichi_5m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan B: {ichi_5m['Senkou span B'].iloc[-2]}, {ichi_5m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan A -26: {ichi_5m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 5m sspan B -26: {ichi_5m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 5m: {ichi_5m['tenkan-sen'].iloc[-2]}. {ichi_5m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 5m: {ichi_5m['kijun-sen'].iloc[-2]}, {ichi_5m['kijun-sen'].iloc[-1]}\n"
                                            f"rsi 10s: {rsi_10s.iloc[-2]}, {rsi_10s.iloc[-1]} \n"
                                            f"adx 10s: {adx_10s['ADX'].iloc[-2]}, {adx_10s['ADX'].iloc[-1]} \n"
                                            f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                            f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                            f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                            f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                            f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                            f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                            f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                            f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                            f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                            "variacion 1\n"
                                            f"venta \n")
                    print("se sale del seguimiento porque se ejecutó operacion")
                    if precio >= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("venta")
                        return
                    elif precio < precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            # Variacion del precio encima del rango al 70%
            elif array_de_precios[0] >= array_de_precios[1] and array_rangos_validos[3]:
                if contador.return_estrategia("venta", "estrategia1") < 2:
                    precio = ejecucion("venta2", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
                    adx_10s = ADX(ohlc_10s)
                    rsi_10s = RSI(ohlc_10s)
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
                    precio2 = array_de_precios[0]
                    ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
                    ichimoku_1m = ichimoku(ohlc_1m)
                    adx_1m = ADX(ohlc_1m)
                    rsi_1m = RSI(ohlc_1m)
                    ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
                    adx_5m = ADX(ohlc_5m)
                    rsi_5m = RSI(ohlc_5m)
                    ichi_5m = ichimoku(ohlc_5m)
                    with open("datos estrategia 1.txt", "at") as fichero_est_1:
                        fichero_est_1.write(f"\nprecio anterior: {ohlc_10s.iloc[-2]} \n"
                                            f"precio actual: {ohlc_10s.iloc[-1]} \n"
                                            f"ichimoku 10s sspan A: {ichimoku_10s['Senkou span A'].iloc[-2]}, {ichimoku_10s['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan B: {ichimoku_10s['Senkou span B'].iloc[-2]}, {ichimoku_10s['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 10s sspan A -26: {ichimoku_10s['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 10s sspan B -26: {ichimoku_10s['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 10s: {ichimoku_10s['tenkan-sen'].iloc[-2]}, {ichimoku_10s['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 10s: {ichimoku_10s['kijun-sen'].iloc[-2]}, {ichimoku_10s['kijun-sen'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A: {ichimoku_1m['Senkou span A'].iloc[-2]}, {ichimoku_1m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan B: {ichimoku_1m['Senkou span B'].iloc[-2]}, {ichimoku_1m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 1m sspan A -26: {ichimoku_1m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 1m sspan B -26: {ichimoku_1m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 1m: {ichimoku_1m['tenkan-sen'].iloc[-2]}. {ichimoku_1m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 1m: {ichimoku_1m['kijun-sen'].iloc[-2]}, {ichimoku_1m['kijun-sen'].iloc[-1]}\n"
                                            f"ichimoku 5m sspan A: {ichi_5m['Senkou span A'].iloc[-2]}, {ichi_5m['Senkou span A'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan B: {ichi_5m['Senkou span B'].iloc[-2]}, {ichi_5m['Senkou span B'].iloc[-1]} \n"
                                            f"ichimoku 5m sspan A -26: {ichi_5m['Senkou span A'].iloc[-26]} \n"
                                            f"ichimoku 5m sspan B -26: {ichi_5m['Senkou span B'].iloc[-26]} \n"
                                            f"tenkan-sen 5m: {ichi_5m['tenkan-sen'].iloc[-2]}. {ichi_5m['tenkan-sen'].iloc[-1]} \n"
                                            f"kijun-sen 5m: {ichi_5m['kijun-sen'].iloc[-2]}, {ichi_5m['kijun-sen'].iloc[-1]}\n"
                                            f"rsi 10s: {rsi_10s.iloc[-2]}, {rsi_10s.iloc[-1]} \n"
                                            f"adx 10s: {adx_10s['ADX'].iloc[-2]}, {adx_10s['ADX'].iloc[-1]} \n"
                                            f"DI+ 10s: {adx_10s['DI+'].iloc[-2]}, {adx_10s['DI+'].iloc[-1]} \n"
                                            f"DI- 10s: {adx_10s['DI-'].iloc[-2]}, {adx_10s['DI-'].iloc[-1]} \n"
                                            f"rsi 1m: {rsi_1m.iloc[-2]}, {rsi_1m.iloc[-1]} \n"
                                            f"adx 1m: {adx_1m['ADX'].iloc[-2]}, {adx_1m['ADX'].iloc[-1]} \n"
                                            f"DI+ 1m: {adx_1m['DI+'].iloc[-2]}, {adx_1m['DI+'].iloc[-1]} \n"
                                            f"DI- 1m: {adx_1m['DI-'].iloc[-2]}, {adx_1m['DI-'].iloc[-1]} \n"
                                            f"rsi 5m: {rsi_5m.iloc[-2]}, {rsi_5m.iloc[-1]} \n"
                                            f"adx 5m: {adx_5m['ADX'].iloc[-2]}, {adx_5m['ADX'].iloc[-1]} \n"
                                            f"DI+ 5m: {adx_5m['DI+'].iloc[-2]}, {adx_5m['DI+'].iloc[-1]} \n"
                                            f"DI- 5m: {adx_5m['DI-'].iloc[-2]}, {adx_5m['DI-'].iloc[-1]} \n"
                                            "variacion 2 \n"
                                            f"venta \n")
                    print("se sale del seguimiento porque se ejecutó operacion")
                    if precio >= precio2:
                        print("operacion ganada, disminuyendo martingala")
                        cambio_de_monto(monto, "disminuir")
                        contador.sumar_estrategia("venta")
                        return
                    elif precio < precio2:
                        print("operacion perdida, aumentando martingala")
                        cambio_de_monto(monto, "aumentar")
                        tiempo_limite = time.time() + 600
            # Se verifica que el dataframe esté actualizado tomando en cuenta el minuto actual y el ultimo
            # minuto del dataframe para actualizar los valores del ichimoku
        #     try:
        #         if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
        #                 ohlc_1m.iloc[-1].name[14:16]):
        #             try:
        #                 ExtraccionOanda(client, 500, 'M1', par)
        #             except Exception as e:
        #                 print(f"excepcion {e}: {type(e)}")
        #                 client = oandapyV20.API(
        #                     access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
        #                     environment="practice")
        #             ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
        #             ichimoku_1m = ichimoku(ohlc_1m)
        #             res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
        #     except Exception as e:
        #         print(f"excepcion {e}: {type(e)}")
        #         print("error en lectura de datos m1 seguimiento ichimoku")
        #     try:
        #         if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
        #                 int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
        #                 (ohlc_5m.iloc[-1].name[
        #                  14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
        #             try:
        #                 ExtraccionOanda(client, 500, 'M5', par)
        #             except Exception as e:
        #                 print(f"excepcion {e}: {type(e)}")
        #                 client = oandapyV20.API(
        #                     access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
        #                     environment="practice")
        #             ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
        #             res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(ohlc_5m, 50)
        #     except Exception as e:
        #         print(f"excepcion {e}: {type(e)}")
        #         print("error en lectura de datos m5 seguimiento ichimoku")
            time.sleep(1)
        print("Se sale del seguimiento porque se ejecutó operación o ",
              (ichimoku_1m["tenkan-sen"].iloc[-2] >= ichimoku_1m["tenkan-sen"].iloc[-1] and
               ichimoku_1m["tenkan-sen"].iloc[-1] <= ichimoku_1m["kijun-sen"].iloc[-1]) and (
                      ichimoku_1m["Senkou span A"].iloc[-2] >= ichimoku_1m["Senkou span A"].iloc[-1]))


def seguimiento_ichimoku2(ohlc_5m, ohlc_1m, ohlc_10s, par, tipo_de_operacion, res_max_30m, res_min_30m, sop_min_30m,
                          sop_max_30m, res_max_5m, res_min_5m, sop_min_5m, sop_max_5m, res_max_1m, res_min_1m,
                          sop_min_1m, sop_max_1m, monto, client, request, contador, array_de_precios,
                          array_rangos_validos):
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
            """
            Indice de valores de los arrays:
                array_de_precios = [ultimo_precio, rango_setenta, rango_treinta]
                array_rangos_validos = [soporte_treinta, resistencia_setenta, soporte_inferior, resistencia_superior]
            """
            print("posible compra, precio:", array_de_precios[0], "resistencia validada:", array_rangos_validos[1],
                  "soporte inferior validado:", array_rangos_validos[2])
            # variación cuando el precio se encuentra en cualquier parte de la parte superior del 70% del
            # rango y el soporte inferior no está validado signigicando un rebote en el precio del rango
            # inferior
            if (not array_rangos_validos[2]) and (not array_rangos_validos[1]):
                if contador.return_estrategia("compra", "estrategia3") < 2:
                    precio = ejecucion("compra1", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
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
                    precio2 = array_de_precios[0]
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
                                            "variacion 1 \n"
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
            # variacion #2 precio debajo del rango 30%
            elif array_de_precios[0] <= array_de_precios[2] and array_rangos_validos[2]:
                if contador.return_estrategia("compra", "estrategia3") <= 2:
                    precio = ejecucion("compra2", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
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
                    precio2 = array_de_precios[0]
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
                                            "variacion 2 \n"
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
            # try:
            #     if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
            #             ohlc_1m.iloc[-1].name[14:16]):
            #         try:
            #             ExtraccionOanda(client, 500, 'M1', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
            #         ichimoku_1m = ichimoku(ohlc_1m)
            #         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
            #     if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
            #             int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
            #             (ohlc_5m.iloc[-1].name[
            #              14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
            #         try:
            #             ExtraccionOanda(client, 500, 'M5', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
            #         res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(ohlc_5m, 50)
            #         adx_5m = ADX(ohlc_5m)
            #         rsi_5m = RSI(ohlc_5m)
            # except Exception as e:
            #     print(f"excepcion {e}: {type(e)}")
            #     print("hubo un error en la lectura de datos 1m o 5m en seguimiento ichimoku 2")
            time.sleep(1)
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
                                                  ichimoku_1m["Senkou span B"].iloc[-26]) and (
                time.time() < tiempo_limite):
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
            """
            Indice de valores de los arrays:
                array_de_precios = [ultimo_precio, rango_setenta, rango_treinta]
                array_rangos_validos = [soporte_treinta, resistencia_setenta, soporte_inferior, resistencia_superior]
            """
            print("posible venta, precio:", array_de_precios[0], "soporte validado:", array_rangos_validos[0],
                  "resistencia superior validada:", array_rangos_validos[3])
            # variación cuando el precio se encuentra en cualquier parte de la parte inferior del 30% del
            # rango y la resistencia superior no está validada signigicando un rebote en el precio del rango
            # superior
            if (not array_rangos_validos[3]) and (not array_rangos_validos[0]):
                if contador.return_estrategia("venta", "estrategia3") <= 2:
                    precio = ejecucion("venta1", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
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
                    precio2 = array_de_precios[0]
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
                                            "variacion 1 \n"
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
            # Variacion #2 precio encima de la resistencia al 70%
            elif array_de_precios[0] >= array_de_precios[1] and array_rangos_validos[3]:
                if contador.return_estrategia("venta", "estrategia3") < 2:
                    precio = ejecucion("venta2", par, tiempo_de_operacion, monto, array_de_precios)
                    if precio == 0:
                        return
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
                    precio2 = array_de_precios[0]
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
                                            "variacion 2 \n"
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
            # try:
            #     if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" !=
            #             ohlc_1m.iloc[-1].name[14:16]):
            #         try:
            #             ExtraccionOanda(client, 500, 'M1', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_1m = pd.read_csv("datos_M1.csv", index_col="time")
            #         ichimoku_1m = ichimoku(ohlc_1m)
            #         res_max_1m, res_min_1m, sop_min_1m, sop_max_1m = calcular_rango_sop_res(ohlc_1m, 10)
            #     if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
            #             int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
            #             (ohlc_5m.iloc[-1].name[
            #              14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
            #         try:
            #             ExtraccionOanda(client, 500, 'M5', par)
            #         except Exception as e:
            #             print(f"excepcion {e}: {type(e)}")
            #             client = oandapyV20.API(
            #                 access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
            #                 environment="practice")
            #         ohlc_5m = pd.read_csv("datos_M5.csv", index_col="time")
            #         res_max_5m, res_min_5m, sop_min_5m, sop_max_5m = calcular_rango_sop_res(ohlc_5m, 50)
            #         adx_5m = ADX(ohlc_5m)
            #         rsi_5m = RSI(ohlc_5m)
            # except Exception as e:
            #     print(f"excepcion {e}: {type(e)}")
            #     print("hubo un error en la lectura de datos 1m o 5m en seguimiento ichimoku 2")
            time.sleep(1)
        if sop_max_5m > ohlc_10s['c'].iloc[-1] > sop_min_5m or sop_max_30m > ohlc_10s['c'].iloc[-1] > sop_min_30m:
            print("Se sale del seguimiento porque hay un soporte cercano")
        else:
            print("se sale del seguimiento porque se ejecutó operacion o ",
                  adx_5m["ADX"].iloc[-1] > 20.0, rsi_5m.iloc[-1] < 70.0,
                  ichimoku_1m["Senkou span A"].iloc[-26] > ohlc_10s['c'].iloc[-1] <
                  ichimoku_1m["Senkou span B"].iloc[-26])
