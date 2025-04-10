from redis_client import redis_client
from utils import mandalorian_episodes
import json

# Buscar si ya existen capítulos en Redis
if not redis_client.keys("capitulo:*"):
    print("No se encontraron capítulos en Redis. Cargando...")

    # Limpia la imagen antes de guardar
    def clean_episode(episode):
        episode.pop("imagen", None)
        return episode

    # Guardar cada capítulo si no está
    for episode in mandalorian_episodes:
        cleaned_episode = clean_episode(episode)
        key = f"capitulo:{episode['temporada']}:{episode['capitulo']}"
        redis_client.set(key, json.dumps(cleaned_episode))

    print("Capítulos cargados correctamente.")
else:
    print("Capítulos ya presentes en Redis. No se cargan nuevamente.")
