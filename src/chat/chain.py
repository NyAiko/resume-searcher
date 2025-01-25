from src.chat.prompt import parser, prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
from langchain_core.documents import Document

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.05)

def selectTheMostRelevant(results:List[Document], jobDescription:str):
    input = {"resumes": results, "jobDescription": jobDescription}
    chain = prompt | llm | parser
    output = chain.invoke(input)
    return output.dict()