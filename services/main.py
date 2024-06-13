from typing import List
from abc import ABC, abstractmethod
from configparser import ConfigParser

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

    def __init__(self,model:str,data:List,temp:float=0.3) ->None:
        self.prompt=f"""The below is text extracted from the bill/invoice form image using AWS/AZURE. 
                        Understand the data and extract the field which I have mentioned below
                        Data: {data}

                        Output Fields:
                            Invoice no
                            GSTIN
                            Name
                            M/s
                            Party's GSTIN
                            E-way Bill No
                            State
                            State code
                            Date
                            Description
                            HSN
                            Unit
                            Rate
                            CGST
                            SGST
                            Igst
                            Total
                            Grand total

                        NOTE: THE OUTPUT SHOULD BE IN JSON FORMAT. 
                        ONLY INCLUDE THE FILEDS WHICH I HAVE MENTIONED IN THE OUTPUT FIELD. 
                        DO NOT RETURN ANY EXTRA TEXT. KEEP IT STRAIGHT TO THE REQUEST."""
        self.model=model
        self.temp=temp
        

    def getLLMResponse(self,extractData:List[dict]):
        pass



