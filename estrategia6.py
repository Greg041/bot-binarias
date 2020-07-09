import pandas as pd
from BollingerBands import boll_bnd
from ADX import ADX
from Ejecucion2 import ejecucion
from multiprocessing import Process
from time import sleep

"""módulo para chequear las condiciones de la estrategia 6 la cual se debe llevar a cabo junto al modulo 
SeguimientoRangos debido a que se debe chequear de forma constante"""


def chequear_estrategia_6(ultimo_precio: float, rango_inferior: float, rango_superior: float, divisa: str,
                          monto, cronometro):
    tiempo_de_operacion_favor = '4'
    tiempo_de_operacion_contra = '4'
    if ultimo_precio >= rango_superior:
        ohlc_1m = pd.read_csv("datos_M1.csv")
        ohlc_5m = pd.read_csv("datos_M5.csv")
        adx_1m = ADX(ohlc_1m)
        adx_5m = ADX(ohlc_5m)
        bollinger_1m = boll_bnd(ohlc_1m)
        bollinger_5m = boll_bnd(ohlc_5m)
        print("bb up: ", bollinger_1m["BB_up"].iloc[-1])
        print(adx_5m["ADX"].iloc[-2] > adx_5m["ADX"].iloc[-1] > 20.0)
        if ultimo_precio > bollinger_1m["BB_up"].iloc[-1] and 30.0 <= adx_1m["DI+"].iloc[-1] > adx_1m["ADX"].iloc[
            -1] >= 20.0 and adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1] and \
            ((bollinger_5m["BB_up"].iloc[-2] < bollinger_5m["BB_up"].iloc[-1] and
              bollinger_5m["BB_dn"].iloc[-2] > bollinger_5m["BB_dn"].iloc[-1]) or
             (bollinger_5m["BB_up"].iloc[-2] > bollinger_5m["BB_up"].iloc[-1] and
              bollinger_5m["BB_dn"].iloc[-2] < bollinger_5m["BB_dn"].iloc[-1])) and \
                (not(adx_5m["ADX"].iloc[-2] > adx_5m["ADX"].iloc[-1] > 20.0)):
            ejecucion_sub = Process(target=ejecucion, args=("compraf", divisa, tiempo_de_operacion_favor,
                                                              monto, ultimo_precio, rango_inferior, rango_superior))
            ejecucion_sub.start()
            print("comienza ejecucion de operacion")
            comienzo_cronometro = Process(target=cronometro.comenzar_cronometro, args=(int(tiempo_de_operacion_favor),))
            comienzo_cronometro.start()
            sleep(5)
        elif ultimo_precio > bollinger_1m["BB_up"].iloc[-1] and adx_1m["DI+"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-2] > adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] > bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] > bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] < bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] < bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion_sub = Process(target=ejecucion, args=("ventac", divisa, tiempo_de_operacion_favor,
                                                            monto, ultimo_precio, rango_inferior, rango_superior))
            ejecucion_sub.start()
            print("comienza ejecucion de operacion")
            comienzo_cronometro = Process(target=cronometro.comenzar_cronometro, args=(int(tiempo_de_operacion_contra),))
            comienzo_cronometro.start()
            sleep(5)
    elif ultimo_precio <= rango_inferior:
        ohlc_1m = pd.read_csv("datos_M1.csv")
        ohlc_5m = pd.read_csv("datos_M5.csv")
        adx_1m = ADX(ohlc_1m)
        adx_5m = ADX(ohlc_5m)
        bollinger_1m = boll_bnd(ohlc_1m)
        bollinger_5m = boll_bnd(ohlc_5m)
        print("bb dn: ", bollinger_1m["BB_dn"].iloc[-1])
        print(adx_5m["ADX"].iloc[-2], adx_5m["ADX"].iloc[-1])
        if ultimo_precio < bollinger_1m["BB_dn"].iloc[-1] and 30.0 <= adx_1m["DI-"].iloc[-1] > adx_1m["ADX"].iloc[
            -1] >= 20.0 and adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] < bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] > bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] > bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] < bollinger_5m["BB_dn"].iloc[-1])) and \
                (not(adx_5m["ADX"].iloc[-2] > adx_5m["ADX"].iloc[-1] > 20.0)):
            ejecucion_sub = Process(target=ejecucion, args=("ventaf", divisa, tiempo_de_operacion_favor,
                                                            monto, ultimo_precio, rango_inferior, rango_superior))
            ejecucion_sub.start()
            print("comienza ejecucion de operacion")
            comienzo_cronometro = Process(target=cronometro.comenzar_cronometro, args=(int(tiempo_de_operacion_favor),))
            comienzo_cronometro.start()
            sleep(5)
        elif ultimo_precio < bollinger_1m["BB_dn"].iloc[-1] and adx_1m["DI-"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-2] > adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] > bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] > bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] < bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] < bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion_sub = Process(target=ejecucion, args=("comprac", divisa, tiempo_de_operacion_favor,
                                                            monto, ultimo_precio, rango_inferior, rango_superior))
            ejecucion_sub.start()
            print("comienza ejecucion de operacion")
            comienzo_cronometro = Process(target=cronometro.comenzar_cronometro,
                                          args=(int(tiempo_de_operacion_contra),))
            comienzo_cronometro.start()
            sleep(5)

