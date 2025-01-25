from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import List

class ResumeFiles(BaseModel):
    filepath: List[str] | None = Field(default = None, title = "Filepath of the resumes")

parser = PydanticOutputParser(pydantic_object=ResumeFiles)
prompt = PromptTemplate(
    template=""" 
                Act as you are a talent recruiter. Which of these these CV/Resume is the most relevant to the job description? 
                These are some resumés found:
                
                {resumes}

                The job description is:
                {jobDescription}

                Please respond with the resume filepath that is the most relevant to the job description. 
                Put only the filepath and only the relevant Resume/CV to the job description

                Your answer must follow this format:
                {format_instructions}

                Return your answer here: 

            """,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
