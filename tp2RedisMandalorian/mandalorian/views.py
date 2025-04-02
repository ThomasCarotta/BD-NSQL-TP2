from django.shortcuts import render
from mandalorian.redis_client import redis_client
import json

# Listar capítulos con búsqueda
def listar_capitulos(request):
    query = request.GET.get("q", "").lower()
    episodios = []

    for temporada in range(1, 4):
        for capitulo in range(1, 9):
            data = redis_client.get(f"capitulo:{temporada}:{capitulo}")
            if data:
                try:
                    cap = json.loads(data)

                    if all(k in cap for k in ["titulo", "temporada", "capitulo", "estado", "descripcion"]):
                        # Filtrar si hay búsqueda
                        if not query or query in cap["titulo"].lower() or query in str(cap["temporada"]) or query in str(cap["capitulo"]):
                            episodios.append(cap)
                    else:
                        print(f"Capítulo {temporada}-{capitulo} tiene datos incompletos: {cap}")

                except json.JSONDecodeError:
                    print(f"Error al decodificar JSON en capitulo:{temporada}:{capitulo}")

    return render(request, "mandalorian/lista_capitulos.html", {"capitulos": episodios})

# Reservar un capítulo por 4 minutos
def reservar_capitulo(request, temporada, capitulo):
    key = f"capitulo:{temporada}:{capitulo}"
    data = redis_client.get(key)

    if data:
        cap = json.loads(data)
        if cap["estado"] == "disponible":
            cap["estado"] = "reservado"
            redis_client.setex(key, 240, json.dumps(cap))  # 4 minutos de reserva
            return render(request, "mandalorian/mensaje.html", {"mensaje": f"Capítulo {capitulo} reservado por 4 minutos."})

    return render(request, "mandalorian/mensaje.html", {"mensaje": "No se pudo reservar el capítulo."})

# Confirmar pago y alquilar por 24 horas
def confirmar_pago(request, temporada, capitulo):
    key = f"capitulo:{temporada}:{capitulo}"
    data = redis_client.get(key)

    if data:
        cap = json.loads(data)
        if cap["estado"] == "reservado":
            cap["estado"] = "alquilado"
            redis_client.setex(key, 86400, json.dumps(cap))  # 24 horas de alquiler
            return render(request, "mandalorian/mensaje.html", {"mensaje": f"Pago confirmado. Capítulo {capitulo} alquilado por 24 horas."})

    return render(request, "mandalorian/mensaje.html", {"mensaje": "Error al confirmar el pago."})
