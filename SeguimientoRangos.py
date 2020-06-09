class SeguimientoRangos:
    def __init__(self):
        self.rango_superior = 0
        self.rango_inferior = 0
        self.posible_nuevo_superior = 0
        self.posible_nuevo_inferior = 0
        self.posible_nuevo_setenta = 0
        self.posible_nuevo_treinta = 0
        self.posible_nuevo_ochenta = 0
        self.posible_nuevo_veinte = 0
        self.rango_ochenta = 0
        self.rango_veinte = 0
        self.rango_setenta = 0
        self.rango_treinta = 0
        self.rango_punto_medio = 0
        self.resistencia_superior_validada = False
        self.soporte_inferior_validada = False
        self.resistencia_setenta_validada = False
        self.soporte_treinta_validada = False
        self.precio_anterior = 0
        self.ultimo_precio = 0
        self.rango_actual_validado = False

    def seguimiento_precio(self, live_data):
        self.precio_anterior = self.ultimo_precio
        self.ultimo_precio = (float(live_data["prices"][0]["closeoutBid"])
                  + float(live_data["prices"][0]["closeoutAsk"])) / 2
        if self.rango_inferior == 0:
            self.establecer_posible_rango(4)
        elif self.ultimo_precio > self.posible_nuevo_superior or self.ultimo_precio < self.posible_nuevo_inferior:
            self.establecer_posible_rango(4)
        self.validar_rango()
        self.check_nuevo_rango()
        self.validar_soporte_resistencia()

    def establecer_posible_rango(self, lugar_digito_pertinente: int):
        self.posible_nuevo_superior = f"{str(self.ultimo_precio)[:lugar_digito_pertinente]}" \
                              f"{int(str(self.ultimo_precio)[lugar_digito_pertinente]) + 1}00"
        self.posible_nuevo_inferior = f"{str(self.ultimo_precio)[:lugar_digito_pertinente]}{str(self.ultimo_precio)[lugar_digito_pertinente]}00"
        self.posible_nuevo_setenta = f"{self.posible_nuevo_inferior[:lugar_digito_pertinente + 1]}{self.posible_nuevo_inferior[(lugar_digito_pertinente+1)].replace('0', '7')}00"
        self.posible_nuevo_treinta = f"{self.posible_nuevo_inferior[:lugar_digito_pertinente + 1]}{self.posible_nuevo_inferior[(lugar_digito_pertinente + 1)].replace('0', '3')}00"
        self.posible_nuevo_ochenta = f"{self.posible_nuevo_inferior[:lugar_digito_pertinente + 1]}{self.posible_nuevo_inferior[(lugar_digito_pertinente + 1)].replace('0', '8')}00"
        self.posible_nuevo_veinte = f"{self.posible_nuevo_inferior[:lugar_digito_pertinente + 1]}{self.posible_nuevo_inferior[(lugar_digito_pertinente + 1)].replace('0', '2')}00"
        self.rango_punto_medio = f"{self.posible_nuevo_inferior[:lugar_digito_pertinente + 1]}{self.posible_nuevo_inferior[(lugar_digito_pertinente + 1)].replace('0', '5')}00"
        self.posible_nuevo_superior, self.posible_nuevo_inferior, self.posible_nuevo_setenta, self.posible_nuevo_treinta, self.rango_punto_medio = \
            float(self.posible_nuevo_superior), float(self.posible_nuevo_inferior), float(self.posible_nuevo_setenta), \
            float(self.posible_nuevo_treinta), float(self.rango_punto_medio)

    def check_nuevo_rango(self):
        if self.posible_nuevo_inferior > self.rango_inferior and self.ultimo_precio >= self.posible_nuevo_treinta:
            self.rango_actual_validado = False
        elif self.posible_nuevo_inferior < self.rango_inferior and self.ultimo_precio <= self.posible_nuevo_setenta:
            self.rango_actual_validado = False

    def validar_rango(self):
        if self.precio_anterior != 0 and self.precio_anterior < self.rango_punto_medio < self.ultimo_precio and \
                self.posible_nuevo_inferior != self.rango_inferior:
            self.rango_actual_validado = True
            self.rango_superior = self.posible_nuevo_superior
            self.rango_inferior = self.posible_nuevo_inferior
            self.rango_setenta = self.posible_nuevo_setenta
            self.rango_treinta = self.posible_nuevo_treinta
            self.rango_ochenta = self.posible_nuevo_ochenta
            self.rango_veinte = self.posible_nuevo_veinte
            self.resistencia_superior_validada = True
            self.soporte_inferior_validada = True
            self.resistencia_setenta_validada = True
            self.soporte_treinta_validada = True
        elif self.precio_anterior != 0 and self.precio_anterior > self.rango_punto_medio > self.ultimo_precio and \
                self.posible_nuevo_inferior != self.rango_inferior:
            self.rango_actual_validado = True
            self.rango_superior = self.posible_nuevo_superior
            self.rango_inferior = self.posible_nuevo_inferior
            self.rango_setenta = self.posible_nuevo_setenta
            self.rango_treinta = self.posible_nuevo_treinta
            self.resistencia_superior_validada = True
            self.soporte_inferior_validada = True
            self.resistencia_setenta_validada = True
            self.soporte_treinta_validada = True

    def validar_soporte_resistencia(self):
        if self.ultimo_precio <= self.rango_treinta and self.rango_actual_validado:
            self.resistencia_setenta_validada = True
            self.soporte_treinta_validada = False
        elif self.ultimo_precio >= self.rango_setenta and self.rango_actual_validado:
            self.resistencia_setenta_validada = False
            self.soporte_treinta_validada = True
        if self.ultimo_precio <= self.rango_inferior:
            self.soporte_inferior_validada = False
        elif self.ultimo_precio >= self.rango_superior:
            self.resistencia_superior_validada = False

