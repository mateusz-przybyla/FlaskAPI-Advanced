from api.extensions import redis_client

def add_jti_to_blocklist(jti: str, exp: int):
    redis_client.setex(f"blocklist:{jti}", exp, "true")

def is_jti_blocked(jti: str) -> bool:
    return redis_client.exists(f"blocklist:{jti}") == 1