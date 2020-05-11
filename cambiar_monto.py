def cambio_de_monto(objeto_monto, aumentar_disminuir):
    if aumentar_disminuir == "aumentar":
        if objeto_monto.monto == "2.00":
            objeto_monto.monto = "2.90"
        elif objeto_monto.monto == "2.90":
            objeto_monto.monto = "2.00"
        # elif objeto_monto.monto == "4.95":
        #     objeto_monto.monto = "1.00"
    elif aumentar_disminuir == "disminuir":
        if objeto_monto.monto == "2.90":
            objeto_monto.monto = "2.00"

