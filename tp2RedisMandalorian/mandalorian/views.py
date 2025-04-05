from django.shortcuts import render, redirect
from mandalorian.redis_client import redis_client
import json
from datetime import datetime, timedelta

# Listar capítulos con verificación de expiraciones
def listar_capitulos(request):
    query = request.GET.get("q", "").lower()
    episodios = []

    for temporada in range(1, 4):
        for capitulo in range(1, 9):
            key = f"capitulo:{temporada}:{capitulo}"
            data = redis_client.get(key)
            if data:
                try:
                    cap = json.loads(data)

                    now = datetime.utcnow()

                    # Verificar si la reserva expiró
                    if cap.get("estado") == "reservado":
                        timestamp = cap.get("timestamp_reserva")
                        if timestamp and now > datetime.utcfromtimestamp(timestamp) + timedelta(minutes=4):
                            cap["estado"] = "disponible"
                            cap.pop("timestamp_reserva", None)
                            redis_client.set(key, json.dumps(cap))

                    # Verificar si el alquiler expiró (1 minuto para testeo)
                    elif cap.get("estado") == "alquilado":
                        timestamp = cap.get("timestamp_alquiler")
                        if timestamp and now > datetime.utcfromtimestamp(timestamp) + timedelta(minutes=1):
                            cap["estado"] = "disponible"
                            cap.pop("timestamp_alquiler", None)
                            redis_client.set(key, json.dumps(cap))

                    if all(k in cap for k in ["titulo", "temporada", "capitulo", "estado", "descripcion"]):
                        if not query or query in cap["titulo"].lower() or query in str(cap["temporada"]) or query in str(cap["capitulo"]):
                            episodios.append(cap)

                except json.JSONDecodeError:
                    print(f"Error al decodificar JSON en {key}")

    return render(request, "mandalorian/lista_capitulos.html", {"capitulos": episodios})


# Reservar un capítulo
def reservar_capitulo(request, temporada, capitulo):
    key = f"capitulo:{temporada}:{capitulo}"
    data = redis_client.get(key)

    if data:
        cap = json.loads(data)
        if cap["estado"] == "disponible":
            cap["estado"] = "reservado"
            cap["timestamp_reserva"] = datetime.utcnow().timestamp()
            redis_client.set(key, json.dumps(cap))

            return render(request, "mandalorian/mensaje.html", {
                "mensaje": f"Capítulo {capitulo} reservado por 4 minutos.",
                "temporada": temporada,
                "capitulo": capitulo,
                "mostrar_botones": True
            })

    return render(request, "mandalorian/mensaje.html", {"mensaje": "No se pudo reservar el capítulo."})


# Confirmar el pago y alquilar
def confirmar_pago(request, temporada, capitulo):
    key = f"capitulo:{temporada}:{capitulo}"
    data = redis_client.get(key)

    if data:
        cap = json.loads(data)
        now = datetime.utcnow()

        if cap.get("estado") == "reservado":
            timestamp = cap.get("timestamp_reserva")
            if timestamp and now <= datetime.utcfromtimestamp(timestamp) + timedelta(minutes=4):
                cap["estado"] = "alquilado"
                cap["timestamp_alquiler"] = now.timestamp()
                cap.pop("timestamp_reserva", None)
                redis_client.set(key, json.dumps(cap))

                return render(request, "mandalorian/mensaje.html", {
                    "mensaje": f"Pago confirmado. Capítulo {capitulo} alquilado.",
                    "regresar": True
                })

            else:
                cap["estado"] = "disponible"
                cap.pop("timestamp_reserva", None)
                redis_client.set(key, json.dumps(cap))
                return render(request, "mandalorian/mensaje.html", {
                    "mensaje": "La reserva expiró. El capítulo volvió a estar disponible.",
                    "regresar": True
                })

    return render(request, "mandalorian/mensaje.html", {
        "mensaje": "No se pudo confirmar el pago.",
        "regresar": True
    })


# Vista del HTML de pago
def pago(request, temporada, capitulo):
    return render(request, "mandalorian/pago.html", {
        "temporada": temporada,
        "capitulo": capitulo
    })
