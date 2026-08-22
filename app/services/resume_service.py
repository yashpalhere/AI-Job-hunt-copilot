from pypdf import PdfReader
from fastapi import UploadFile
from app.schemas.resume import ResumeParsed
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
llm  = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")
struc_llm= llm.with_structured_output(ResumeParsed)
prompt = ChatPromptTemplate.from_messages([
        ('system' ,"""You are a resume parser.Extract the candidate's technical and professional skillsand provide a concise summary of their experience."""),("human","Resume \n {resume_text}")
    ])
chain = prompt | struc_llm

def extract_resume_text (resume : UploadFile):
    reader = PdfReader(resume.file)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

def parse_resume(raw_text: str) -> ResumeParsed:
    result = chain.invoke({"resume_text": raw_text})
    return result
