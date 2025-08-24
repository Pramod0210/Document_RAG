import os
import sys
from utils.model_loader import ModelLoader
from exception.custom_exception import CustomException
from logger.custom_logger import CustomLogger
from model.models import *
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyzer:
    def __init__(self):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()
            self.llm = self.model_loader.load_llm()
            self.log.info("DocumentAnalyzer initialized with embeddings and LLM.")
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(
                llm=self.llm,
                parser=self.parser
            )

            self.prompt = PROMPT_REGISTRY["document_analysis"]

        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {str(e)}")
            raise CustomException(f"Failed to initialize DocumentAnalyzer: {str(e)}", sys)
        
    def analyze_document(self, document_text: str) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm | self.fixing_parser

            self.log.info("Meta Data Chain Initialized...")

            resposne = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })
            self.log.info("Document analysis completed successfully.")
            return resposne
        except Exception as e:
            self.log.error(f"Error analyzing document: {str(e)}")
            raise CustomException(f"Failed to analyze document: {str(e)}", sys)




