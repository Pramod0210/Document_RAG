import sys
import os
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from model.models import *
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY


class DocumentCompareLLM:
    def __init__(self):
        try:            
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()
            self.llm = self.model_loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
            self.fixing_parser = OutputFixingParser.from_llm(
                parser=self.parser,
                llm=self.llm
            )

            self.prompt = PROMPT_REGISTRY["document_comparison"]
            self.chain = self.prompt | self.llm | self.parser
            self.log.info("DocumentCompareLLM initialized with model and parser.")


        except Exception as e:
            self.log.error(f"Error initializing DocumentCompareLLM: {str(e)}")
            raise CustomException(f"Failed to initialize DocumentCompareLLM: {str(e)}", sys)

    
    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        try:
            inputs = {
                "format_instructions": self.parser.get_format_instructions(),
                "combined_docs": combined_docs
            }
            self.log.info(f"Inputs for document comparison: {inputs}")

            response = self.chain.invoke(inputs)
            self.log.info(f"Document comparison response: {response}")

            return self._format_response(response)


        except Exception as e:
            self.log.error(f"Error comparing documents: {str(e)}")
            raise CustomException(f"Failed to compare documents: {str(e)}", sys)
        

    def _format_response(self, response: list[dict]) -> pd.DataFrame:
        try:
            df = pd.DataFrame(response)
            self.log.info(f"Formatted response into DataFrame:", dataframe=df)
            return df
        except Exception as e:
            self.log.error(f"Error formatting response into DataFrame: {str(e)}")
            raise CustomException(f"Failed to format response into DataFrame: {str(e)}", sys)
        
    
