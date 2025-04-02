import redis

redis_client = redis.StrictRedis(
    host='localhost',  # O '172.18.0.1'
    port=6379,  
    db=0,
    decode_responses=True  # Para recibir strings en lugar de bytes
)
