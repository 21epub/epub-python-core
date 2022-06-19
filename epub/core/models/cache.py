from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet

TTL_ONE_DAY = 3600 * 24


class CacheModelMixin(object):
    @classmethod
    def __get_cache_key(cls, unique_key, unique_value):
        return f"CacheModelMixin:{cls._meta.db_table}:{unique_key}:{unique_value}"

    @classmethod
    def get_instance_from_cache(cls, unique_key, unique_value):
        cache_key = cls.__get_cache_key(unique_key, unique_value)
        return cache.get(cache_key)

    def set_cache(self, unique_key="pk"):
        cache_key = self.__get_cache_key(unique_key, getattr(self, unique_key))
        cache.set(cache_key, self, TTL_ONE_DAY)

    def delete_cache(self, unique_key="pk"):
        cache_key = self.__get_cache_key(unique_key, getattr(self, unique_key))
        cache.delete(cache_key)

    def save(self, **kwargs):
        super().save(**kwargs)

        if hasattr(self, "UNIQUE_KEYS"):
            unique_keys = getattr(self, "UNIQUE_KEYS")
            for unique_key in unique_keys:
                self.set_cache(unique_key=unique_key)
        else:
            raise RuntimeError("Model must define `UNIQUE_KEYS`")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        if hasattr(self, "UNIQUE_KEYS"):
            unique_keys = getattr(self, "UNIQUE_KEYS")
            for unique_key in unique_keys:
                self.delete_cache(unique_key=unique_key)
        else:
            raise RuntimeError("Model must define `unique_keys`")


class CacheQuerySet(QuerySet):
    def get(self, *args, **kwargs):
        if len(kwargs.keys()) == 1:
            instance = None
            for unique_key, unique_value in kwargs.items():
                instance = self.model.get_instance_from_cache(unique_key, unique_value)
                break

            if not instance:
                instance = super().get(*args, **kwargs)
                instance.set_cache(unique_key)
        else:
            # More than one kwargs.
            instance = super().get(*args, **kwargs)
        return instance
