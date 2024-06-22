from typing import List,Dict
from abc import ABC, abstractmethod
from configparser import ConfigParser
import json

class ExtractStrategyWrapper(ABC):
    def __init__(self,config_type:str) -> None:
        config=ConfigParser()
        config.read("../config/config.ini")
        self.config=config[config_type]
        
    @abstractmethod
    def extract(self,file_path:str)->dict:
        #implementation should be in implementation class
        pass

    def convert_pdf_to_img(self,pdf_file_path:str)->None:
        pass


class LLM():

    def __init__(self, config_type:str) ->None:
        config=ConfigParser()
        config.read("config\config.INI")
        self.config=config[config_type]
                
    def getLLMResponse(self,extractData:List[dict]):
        pass

    def constructDictResponse(self,response:str):
        pass
