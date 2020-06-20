import pandas as pd
from BollingerBands import boll_bnd
from ADX import ADX
from Ejecucion import ejecucion
"""módulo para chequear las condiciones de la estrategia 6 la cual se debe llevar a cabo junto al modulo 
SeguimientoRangos debido a que se debe chequear de forma constante"""


def chequear_estrategia_6(ultimo_precio: float, rango_inferior: float, rango_superior: float, divisa: str, monto: str):
    tiempo_de_operacion_favor = '4'
    tiempo_de_operacion_contra = '4'
    if ultimo_precio >= rango_superior:
        ohlc_1m = pd.read_csv("datos_M1.csv")
        ohlc_5m = pd.read_csv("datos_M5.csv")
        adx_1m = ADX(ohlc_1m)
        bollinger_1m = boll_bnd(ohlc_1m)
        bollinger_5m = boll_bnd(ohlc_5m)
        print("bb up: ", bollinger_1m["BB_up"].iloc[-1], "bb dn: ", bollinger_1m["BB_dn"].iloc[-1])
        if ultimo_precio > bollinger_1m["BB_up"].iloc[-1] and adx_1m["DI+"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-1] >= 20.0 and adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1] and \
            ((bollinger_5m["BB_up"].iloc[-2] <= bollinger_5m["BB_up"].iloc[-1] and
              bollinger_5m["BB_dn"].iloc[-2] >= bollinger_5m["BB_dn"].iloc[-1]) or
             (bollinger_5m["BB_up"].iloc[-2] >= bollinger_5m["BB_up"].iloc[-1] and
              bollinger_5m["BB_dn"].iloc[-2] <= bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion("compraf", divisa, tiempo_de_operacion_favor, monto)
        elif ultimo_precio < bollinger_1m["BB_up"].iloc[-1] and adx_1m["DI+"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-2] > adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] >= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] >= bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] <= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] <= bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion("ventac", divisa, tiempo_de_operacion_contra, monto)
    if ultimo_precio <= rango_inferior:
        if ultimo_precio < bollinger_1m["BB_dn"].iloc[-1] and adx_1m["DI-"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-1] >= 20.0 and adx_1m["ADX"].iloc[-2] < adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] <= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] >= bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] >= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] <= bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion("ventaf", divisa, tiempo_de_operacion_favor, monto)
        elif ultimo_precio < bollinger_1m["BB_dn"].iloc[-1] and adx_1m["DI-"].iloc[-1] >= 30.0 and \
                adx_1m["ADX"].iloc[-2] > adx_1m["ADX"].iloc[-1] and \
                ((bollinger_5m["BB_up"].iloc[-2] >= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] >= bollinger_5m["BB_dn"].iloc[-1]) or
                 (bollinger_5m["BB_up"].iloc[-2] <= bollinger_5m["BB_up"].iloc[-1] and
                  bollinger_5m["BB_dn"].iloc[-2] <= bollinger_5m["BB_dn"].iloc[-1])):
            ejecucion("comprac", divisa, tiempo_de_operacion_contra, monto)
