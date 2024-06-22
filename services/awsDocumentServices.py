from main import ExtractStrategyWrapper,LLM
import os,re,json
from textractor import Textractor
from textractor.data.constants import TextractFeatures
import pypdfium2 as pdfium
from typing import List,Dict
import google.generativeai as genai

class AwsExtractStrategy(ExtractStrategyWrapper):

    def __init__(self):
        os.environ['AWS_CONFIG_FILE'] = 'C:/Users\ASUS\MyWorks\Projects\GSTExtract\config\config.INI'
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
    def __init__(self, config_type:str):
        super().__init__(config_type)

        self.api_key = self.config['api_key']
        genai.configure(api_key=self.config['api_key'])

        self.model = self.config['model']
        self.temperature = self.config['temperature']
        self.top_p = self.config['top_p']
        self.top_k = self.config['top_k']
        self.max_output_tokens = self.config['max_output_tokens']
        self.response_mime_type = self.config['response_mime_type']

        self.generation_config = {
                                "temperature": float(self.temperature),
                                "top_p": int(self.top_p),
                                "top_k": int(self.top_k),
                                "max_output_tokens": int(self.max_output_tokens),
                                "response_mime_type": str(self.response_mime_type),
                                }
        
    def constructDictResponse(self,response:str):
        try:
            try:
                response = response.strip("```JSON\n```")
            except Exception as e:
                pass

            pattern = r'"([^"]+)"\s*:\s*"([^"]*)"|(\w+)\s*:\s*(null)'
            matches = re.findall(pattern, response)
            result = {}
            for match in matches:
                if match[0] and match[1]:
                    result[match[0]] = match[1]
                elif match[2]:
                    result[match[2]] = None

            result = json.dumps(result, indent=2) 
            return result
        
        except Exception as e:
            print("Error parsing the response, Returning the raw text response back")
            return response
        
    def getLLMResponse(self,data:List[str])->str:

        data = f"""{data}"""
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

        model = genai.GenerativeModel(
                                        model_name = self.model,
                                        generation_config = self.generation_config,
                                    )
        
        chat_session = model.start_chat(
                                            history=[]
                                       )
        response = chat_session.send_message(str(self.prompt))

        response = self.constructDictResponse(response.text)

        return response
    

aws = AwsExtractStrategy()
extracted_data = aws.extract("C:/Users\ASUS\MyWorks\Projects\GSTExtract\storage\IMG-20240601-WA0024.jpg")

aws_gpt  = awsLLM('GEMINI')

transformed_data = aws_gpt.getLLMResponse(extracted_data)
print(transformed_data)
