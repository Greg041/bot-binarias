from ExtraccionDatosOanda import ExtraccionOanda
from analisis_y_estrategia import analisis_y_estrategia, analisis_y_estrategia_2_2, \
    analisis_y_estrategia_2_3, analisis_y_estrategia3
from multiprocessing import Process
from ExtraccionDatos10s import extraccion_10s_continua
import time
import pandas as pd


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


def run(tiempo_de_ejecucion_minutos, primera_divisa, segunda_divisa, tipo_de_est, numero_noticias,
        horas_noticias):
    print("comenzando")
    timeout = time.time() + (tiempo_de_ejecucion_minutos * 60)
    divisa = f"{primera_divisa}_{segunda_divisa}"
    proceso_1_min = ExtraccionOanda(500, "M1", f"{primera_divisa}_{segunda_divisa}")
    proceso_5_min = ExtraccionOanda(120, "M5", f"{primera_divisa}_{segunda_divisa}")
    proceso_10s = Process(target=extraccion_10s_continua, args=(divisa,))
    proceso_1_min.start()
    proceso_5_min.start()
    proceso_10s.start()
    time.sleep(30)
    datos_1min = pd.read_csv("datos_M1.csv", index_col="time")
    # Se calcula el rango de soporte y resistencia de 1 minuto a un rango de 150 velas
    resistencia_punto_mayor_1m, resistencia_punto_menor_1m, soporte_punto_menor_1m, soporte_punto_mayor_1m = \
        calcular_rango_sop_res(datos_1min, 120)
    datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
    # Se calcula el rango de soporte y resistencia de 5 minuto a un rango de 50 velas
    resistencia_punto_mayor_5m, resistencia_punto_menor_5m, soporte_punto_menor_5m, soporte_punto_mayor_5m = \
        calcular_rango_sop_res(datos_5min, 50)
    while time.time() <= timeout:
        try:
            if numero_noticias == 1:
                if time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[0]:
                    time.sleep(3600)
            elif numero_noticias == 2:
                if time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[0]:
                    time.sleep(3600)
                elif time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[1]:
                    time.sleep(3600)
            elif numero_noticias == 3:
                if time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[0]:
                    time.sleep(3600)
                elif time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[1]:
                    time.sleep(3600)
                elif time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[:-3] == horas_noticias[2]:
                    time.sleep(3600)
            if (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                datos_1min.iloc[-1].name[14:16]) and \
                    (f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16])):02}" != \
                     datos_1min.iloc[-1].name[14:16]):
                datos_1min = pd.read_csv("datos_M1.csv", index_col="time")
                resistencia_punto_mayor_1m, resistencia_punto_menor_1m, soporte_punto_menor_1m, soporte_punto_mayor_1m = \
                    calcular_rango_sop_res(datos_1min, 120)
            if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                    int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                    (datos_5min.iloc[-1].name[
                     14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1:02}"):
                datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
                resistencia_punto_mayor_5m, resistencia_punto_menor_5m, soporte_punto_menor_5m, soporte_punto_mayor_5m = \
                    calcular_rango_sop_res(datos_5min, 50)
            datos_10s = pd.read_csv("datos_10s.csv", index_col="time")
        except:
            print("hubo error en lectura de datos csv")
        if tipo_de_est == "todo":
            analisis_y_estrategia(datos_10s, datos_1min, datos_5min, divisa, resistencia_punto_mayor_1m,
                                   resistencia_punto_menor_1m, resistencia_punto_mayor_5m,
                                   resistencia_punto_menor_5m, soporte_punto_menor_1m, soporte_punto_mayor_1m,
                                   soporte_punto_menor_5m, soporte_punto_mayor_5m)
        elif tipo_de_est == "favor":
            analisis_y_estrategia_2_2(datos_1min, divisa, resistencia_punto_mayor_1m, resistencia_punto_menor_1m,
                                      resistencia_punto_mayor_5m, resistencia_punto_menor_5m,
                                      soporte_punto_menor_1m, soporte_punto_mayor_1m, soporte_punto_menor_5m,
                                      soporte_punto_mayor_5m)
        elif tipo_de_est == "contra":
            analisis_y_estrategia_2_3(datos_10s, datos_1min, divisa, resistencia_punto_mayor_1m,
                                      resistencia_punto_menor_1m,
                                      resistencia_punto_mayor_5m, resistencia_punto_menor_5m,
                                      soporte_punto_menor_1m, soporte_punto_mayor_1m, soporte_punto_menor_5m,
                                      soporte_punto_mayor_5m)
        time.sleep(5)


if __name__ == "__main__":
    primera_divisa = input("introduzca la primera divisa: ")
    segunda_divisa = input("introduzca la segunda divisa: ")
    tipo_de_estrategia = input("estategia en contra, favor o todo?: ")
    mes = input("introduzca el mes de inicio: ")
    dia = input("introduzca el dia de inicio: ")
    hora = input("introduzca la hora de inicio (militar): ")
    minuto = input("introduzca el minuto de inicio: ")
    tiempo = int(input("introduzca el tiempo de ejecucion en minutos: "))
    numero_noticias = int(input("Introduzca el numero de noticias: "))
    noticia1 = 0
    noticia2 = 0
    noticia3 = 0
    if numero_noticias == 0:
        pass
    elif numero_noticias == 1:
        hora_noticia = input("Introduzca la hora de la noticia 30 minutos antes: ")
        minuto_noticia = input("Introduzca el minuto de la noticia 30 minutos antes: ")
        noticia1 = f'2020-{mes}-{dia} {hora_noticia}:{minuto_noticia}'
    elif numero_noticias == 2:
        hora_noticia1 = input("Introduzca la hora de la primera noticia 30 minutos antes: ")
        minuto_noticia1 = input("Introduzca el minuto de la primera noticia 30 minutos antes: ")
        noticia1 = f'2020-{mes}-{dia} {hora_noticia1}:{minuto_noticia1}'
        hora_noticia2 = input("Introduzca la hora de la segunda noticia 30 minutos antes: ")
        minuto_noticia2 = input("Introduzca el minuto de la segunda noticia 30 minutos antes: ")
        noticia2 = f'2020-{mes}-{dia} {hora_noticia2}:{minuto_noticia2}'
    elif numero_noticias == 3:
        hora_noticia1 = input("Introduzca la hora de la primera noticia 30 minutos antes: ")
        minuto_noticia1 = input("Introduzca el minuto de la noticia 30 minutos antes: ")
        noticia1 = f'2020-{mes}-{dia} {hora_noticia1}:{minuto_noticia1}'
        hora_noticia2 = input("Introduzca la hora de la segunda noticia 30 minutos antes: ")
        minuto_noticia2 = input("Introduzca el minuto de la segunda noticia 30 minutos antes: ")
        noticia2 = f'2020-{mes}-{dia} {hora_noticia2}:{minuto_noticia2}'
        hora_noticia3 = input("Introduzca la hora de la tercera noticia 30 minutos antes: ")
        minuto_noticia3 = input("Introduzca el minuto de la tercera noticia 30 minutos antes: ")
        noticia3 = f'2020-{mes}-{dia} {hora_noticia1}:{minuto_noticia1}'
    while time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) != f'2020-{mes}-{dia} {hora}:{minuto}:00':
        pass
    run(tiempo, primera_divisa, segunda_divisa, tipo_de_estrategia, numero_noticias,
        (noticia1, noticia2, noticia3))
