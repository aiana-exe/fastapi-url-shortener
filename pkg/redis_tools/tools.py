import redis


class RedisTools:

    __redis_connect = redis.Redis(host='redis', port=6379)

    @classmethod
    def set_pair(cls, original_url: str, shortened_url: str):

        cls.__redis_connect.set(original_url, shortened_url)

    @classmethod
    def get_value(cls, original_url):

        return cls.__redis_connect.get(original_url)
    
    @classmethod
    def get_keys(cls):
        return cls.__redis_connect.keys(pattern='*')
    
    
    @classmethod
    def get_keys_and_values(cls):
        keys = cls.get_keys()
        values = cls.__redis_connect.mget(keys)
        return dict(zip([key.decode('utf-8') for key in keys], [value.decode('utf-8') if value else None for value in values]))