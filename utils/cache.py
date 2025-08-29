# from langchain.cache import InMemoryCache
# from langchain.globals import set_llm_cache

# llm_cache = InMemoryCache()
# set_llm_cache(llm_cache)


from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache
from logger.custom_logger import CustomLogger

log = CustomLogger().get_logger(__name__)

class LoggingInMemoryCache(InMemoryCache):
    def lookup(self, prompt, llm_string):
        result = super().lookup(prompt, llm_string)
        if result is not None:
            log.info(f"Cache hit for prompt: {prompt[:50]}...")
        else:
            log.info(f"Cache miss for prompt: {prompt[:50]}...")
        return result

    def update(self, prompt, llm_string, result):
        log.info(f"Cache update for prompt: {prompt[:50]}...")
        return super().update(prompt, llm_string, result)

llm_cache = LoggingInMemoryCache()
set_llm_cache(llm_cache)