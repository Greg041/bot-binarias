def cambio_de_monto(objeto_monto, aumentar_disminuir):
    if aumentar_disminuir == "aumentar":
        if objeto_monto.monto == "1.00":
            objeto_monto.monto = "1.45"
        elif objeto_monto.monto == "1.45":
            objeto_monto.monto = "2.10"
        elif objeto_monto.monto == "2.10":
            objeto_monto.monto = "1.00"
    elif aumentar_disminuir == "disminuir":
        if objeto_monto.monto == "1.00":
            pass
        elif objeto_monto.monto == "1.45":
            objeto_monto.monto = "1.00"
        elif objeto_monto.monto == "2.10":
            objeto_monto.monto = "1.45"
