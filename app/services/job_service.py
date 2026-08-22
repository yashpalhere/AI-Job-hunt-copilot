from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.job import JobParsed
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash")
structured_llm = llm.with_structured_output(JobParsed)
prompt = ChatPromptTemplate.from_messages([
    ("system","""You are a job description parser.
            Extract the company name, job role, and required technical
            and professional skills from the provided job description."""
    ),("human","Company: {company} \n Role: {role} \n Job Description:\n{jd_text}")
])
chain = prompt | structured_llm
def parse_job (  company: str, role: str,jd_text : str) -> JobParsed:
    result = chain.invoke ( { "company": company,"role": role,"jd_text": jd_text})
    return result 

