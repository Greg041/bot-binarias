"""
Clase que se encarga de mantener un registro de cuantas veces se ha ejecutado una estrategia de forma seguida
y que tipo de operación ejecutó, sea esta compra o venta

return_estrategia: se encarga de revisar de que estrategia es la operación está a punto de ejecutarse
y revisar si es la misma estrategia que se ejecutó en la ocasión anterior además de si es el mismo tipo de
operación, si no es la misma estrategia entonces el método se encargará de reiniciar los contadores de compra
y venta llamando a la función "resetear contadores".

sumar_estrategia: se encarga de aumentar el contador de compra o venta de la última estrategia ejecutada
"""

class ContadorEstrategias:
    def __init__(self):
        self.ultima_estrategia = ""  # registro de la última estrategia que dio una señal
        self.repeticion_compra = 0
        self.repeticion_venta = 0

    def resetear_contadores(self):
        self.repeticion_compra = 0
        self.repeticion_venta = 0

    def return_estrategia(self, tipo_de_operacion: str, estrategia: str):
        if estrategia == self.ultima_estrategia:
            if tipo_de_operacion == "compra":
                return self.repeticion_compra
            else:
                return self.repeticion_venta
        else:
            self.ultima_estrategia = estrategia
            self.resetear_contadores()
            if tipo_de_operacion == "compra":
                return self.repeticion_compra
            else:
                return self.repeticion_venta

    def sumar_estrategia(self, tipo_de_operacion: str):
        if tipo_de_operacion == "compra":
            self.repeticion_compra += 1
            return self.repeticion_compra
        elif tipo_de_operacion == "venta":
            self.repeticion_venta += 1
            return self.repeticion_venta
