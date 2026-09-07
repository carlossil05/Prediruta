import math

def haversine_distance(coord1, coord2):
    R = 6371.0
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def interpolar_punto(p1, p2, fraccion):
    return (p1[0] + (p2[0] - p1[0]) * fraccion, p1[1] + (p2[1] - p1[1]) * fraccion)

def segmentar_ruta(puntos_full, tamano_tramo_km):
    if not puntos_full or len(puntos_full) < 2:
        return [puntos_full] if puntos_full else []

    tramos, tramo_actual, dist_acumulada = [], [puntos_full[0]], 0.0

    for i in range(len(puntos_full) - 1):
        p_inicio, p_fin = puntos_full[i], puntos_full[i+1]
        dist_segmento = haversine_distance(p_inicio, p_fin)
        if dist_segmento == 0:
            continue

        p_cursor, dist_restante = p_inicio, dist_segmento

        while dist_acumulada + dist_restante >= tamano_tramo_km:
            necesario = tamano_tramo_km - dist_acumulada
            p_corte = interpolar_punto(p_cursor, p_fin, necesario / dist_restante)
            tramo_actual.append(p_corte)
            tramos.append(tramo_actual)
            tramo_actual, dist_acumulada, p_cursor = [p_corte], 0.0, p_corte
            dist_restante = haversine_distance(p_cursor, p_fin)

        if dist_restante > 0:
            tramo_actual.append(p_fin)
            dist_acumulada += dist_restante

    if len(tramo_actual) > 1:
        tramos.append(tramo_actual)

    return tramos