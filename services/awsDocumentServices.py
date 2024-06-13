from main import ExtractStrategyWrapper,LLM
import os
from textractor import Textractor
from textractor.data.constants import TextractFeatures
import pypdfium2 as pdfium
from typing import List
from openai import OpenAI
from configparser import ConfigParser

class AwsExtractStrategy(ExtractStrategyWrapper):

    def __init__(self):
        os.environ['AWS_CONFIG_FILE'] = 'C:/Users/ASUS/MyWorks/Projects/BillExtraction/config.ini'
        self.extractor = Textractor(profile_name="default")

    def contains_pdf(self, file_string: str) -> bool:
        file_string = file_string.lower()
        return '.pdf' in file_string
    
    def convert_pdf_to_img(self,pdf_file_path:str)->List:

        specific_path_list = []
        specific_path_output = []

        if not os.path.exists("Ticket"):
            os.makedirs("Ticket")
            
        pdf = pdfium.PdfDocument(pdf_file_path)
        
        for i in range(len(pdf)):
            page = pdf[i]
            image = page.render(scale=3).to_pil()
            specific_path = f"Ticket/{i}.jpg"
            image.save(specific_path)
            specific_path_list.append(specific_path)

        for i in specific_path_list:
            specific_output = self.extract(i)
            specific_path_output.append(specific_output)
            os.remove(i)

        return specific_path_output
    
    def extract(self,path:str)->List:

        if not(self.contains_pdf(path)):
            
            document = self.extractor.analyze_document(
                file_source = path,
                features=TextractFeatures.LAYOUT
            )
            output = document.lines 

            return output
        
        else:

            output = self.convert_pdf_to_img(path)

            return output[0]



class awsLLM(LLM):
    def __init__(self, data: List):
        self.data = data
        self.model = "gpt-3.5-turbo"

        super().__init__(self.model,self.data)

        self.client = OpenAI(api_key="<api-key>")
        
    def getLLMResponse(self):
        
        completion = self.client.chat.completions.create(
        model="gpt-3.5-turbo",

        messages=[
            {"role": "system", "content": "You are a good data extractor. Extract the data from the raw as mentioned. Do not return any unwanted text"},
            {"role": "user", "content": self.prompt}
                ]
        )

        return completion.choices[0].message
    

aws = AwsExtractStrategy()
extracted_data = aws.extract("D:/Ticket.pdf")

aws_gpt  = awsLLM(extracted_data)
transformed_data = aws_gpt.getLLMResponse()