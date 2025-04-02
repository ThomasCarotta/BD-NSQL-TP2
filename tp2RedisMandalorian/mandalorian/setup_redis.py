from mandalorian.redis_client import redis_client
from mandalorian.utils import mandalorian_episodes
import json

# Eliminar solo los episodios existentes en Redis antes de actualizar
for key in redis_client.keys("capitulo:*"):
    redis_client.delete(key)

# Insertar los episodios sin la clave de imagen
def clean_episode(episode):
    episode.pop("imagen", None)  # Elimina la clave "imagen" si existe
    return episode

for episode in mandalorian_episodes:
    cleaned_episode = clean_episode(episode)
    redis_client.set(f"capitulo:{episode['temporada']}:{episode['capitulo']}", json.dumps(cleaned_episode))

print("Capítulos actualizados en Redis sin imágenes.")
