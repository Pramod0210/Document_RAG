import os
import sys
from dotenv import load_dotenv
from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

log = CustomLogger().get_logger(__name__)

class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("api_keys")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("Missing required API keys", missing_keys=missing)
            raise CustomException("Missing API keys", sys)

        log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """

    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))
    
    def _validate_env(self):
        required_api_keys = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.api_keys = {key: os.getenv(key) for key in required_api_keys}
        missing_keys = [key for key, value in self.api_keys.items() if not value]
        if missing_keys:
            log.error(f"Missing required environment variables: {', '.join(missing_keys)}")
            raise CustomException(f"Missing environment variables:", sys)
        log.info("All required environment variables are set.")

    def load_embeddings(self):
        try:
            log.info("Loading embeddings...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(
                model=model_name
            )

        except Exception as e:
            log.error(f"Error loading embedding model:", error = str(e))
            raise CustomException(f"Failed to load embedding model:", sys)
        
    def load_llm(self):

        log.info(f"Loading LLM with configuration")
        llm_block = self.config["llm"]

        provider_key = os.getenv("LLM_PROVIDER", "groq")
        print('provider_key:', provider_key)
        
        if provider_key not in llm_block:
            log.error(f"Provider key {provider_key} not found in LLM configuration.")
            raise CustomException(f"Provider key {provider_key} not found in LLM configuration.", sys)
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.1)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info(f"Loading LLM Model Provider : {provider}, Model Name: {model_name}, Temperature: {temperature}, Max Output Tokens: {max_tokens}")

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        
        elif provider == "groq":
            return ChatGroq(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:           
            log.error(f"Unsupported provider: {provider}")
            raise CustomException(f"Unsupported provider: {provider}", sys)

if __name__ == "__main__":
    loader = ModelLoader()
    embeddings = loader.load_embeddings()
    llm = loader.load_llm()
    result = llm.invoke("What is the capital of France?")
    log.info(f"LLM Invocation Result: {result}")




