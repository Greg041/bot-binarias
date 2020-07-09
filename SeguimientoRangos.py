from estrategia6 import chequear_estrategia_6
from multiprocessing import Value

class SeguimientoRangos:
    def __init__(self):
        self.rango_superior = 0
        self.rango_inferior = 0
        self.estrategia_6_check = False
        self.precio_anterior = 0
        self.ultimo_precio = Value('d', 0.0)

    def seguimiento_precio(self, live_data, divisa, monto, cronometro):
        self.precio_anterior = self.ultimo_precio.value
        self.ultimo_precio.value = (float(live_data["prices"][0]["closeoutBid"])
                  + float(live_data["prices"][0]["closeoutAsk"])) / 2
        print(self.ultimo_precio.value)
        if self.rango_inferior == 0:
            self.establecer_rango_inicial(4)
        print("cronometro:", cronometro.retornar_cronometro())
        if cronometro.retornar_cronometro() == 0:
            chequear_estrategia_6(self.ultimo_precio.value, self.rango_inferior, self.rango_superior,
                                                        divisa, monto, cronometro)
        self.check_nuevo_rango()

    def establecer_rango_inicial(self, lugar_digito_pertinente: int):
        self.rango_superior = float(f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}") \
        + 0.001
        self.rango_inferior = float(f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}") \
        - 0.001
        print(self.rango_superior, self.rango_inferior)

    def establecer_rango(self, lugar_digito_pertinente: int):
        if self.ultimo_precio.value >= self.rango_superior:
            self.rango_superior = float(
                f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}") \
                                  + 0.001
            self.rango_inferior = float(
                f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}") \
                                  - 0.001
        elif self.ultimo_precio.value <= self.rango_inferior:
            self.rango_superior = float(
                f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}") \
                                  + 0.002
            self.rango_inferior = float(
                f"{str(self.ultimo_precio.value)[:lugar_digito_pertinente]}{str(self.ultimo_precio.value)[lugar_digito_pertinente]}00")
        print(self.rango_superior, self.rango_inferior)

    def check_nuevo_rango(self):
        if self.ultimo_precio.value >= self.rango_superior:
            self.establecer_rango(4)
        elif self.ultimo_precio.value <= self.rango_inferior:
            self.establecer_rango(4)


