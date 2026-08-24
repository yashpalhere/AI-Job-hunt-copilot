from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import numpy as np
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.models.resume_chunk import ResumeChunk
from app.schemas.llm import RAGResponse
from app.models.job import Job
load_dotenv()
from app.database.database import session_local

embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")


def retrieve_relevant_information(resume_id: int,query: str,db: Session,k: int = 5):
    query_embedding = embedding_model.embed_query(query)
    sementic_retrieved_Resumechunk_objects = (db.query(ResumeChunk).filter(ResumeChunk.resume_id == resume_id).order_by(ResumeChunk.embedding.cosine_distance(query_embedding)).limit(k*3).all())

    if not sementic_retrieved_Resumechunk_objects:
        return []
    chunk_embeddings = [ chunk.embedding for chunk in sementic_retrieved_Resumechunk_objects]
    selected_indices = mmr(chunk_embeddings,query_embedding,k)
    return [sementic_retrieved_Resumechunk_objects[chunk_idx] for chunk_idx in selected_indices]

def mmr(chunk_embeddings, query_embedding, k=4,lambda_mult = 0.7):
    query_embedding = np.array(query_embedding)
    chunk_embeddings = np.array(chunk_embeddings)

    selected =[]
    remaining = list(range(len(chunk_embeddings)))
    #similarity of query with most relevent chunk 
    query_magnitude = np.linalg.norm ( query_embedding)
    chunk_magnitudes = np.linalg.norm ( chunk_embeddings,axis=1)

    query_similarities = ( (chunk_embeddings @ query_embedding) / (query_magnitude * chunk_magnitudes) )
    first = int(np.argmax(query_similarities)) #argmax gives the index of max value and this type casting done cause the np.argmax return numpy.64 etc datatypes not python int so for compatibility we use int()
    selected.append(first)
    remaining.remove(first)

    while remaining and len(selected)<k:
        best_index = None
        best_score = -float("inf")
        for chunk_idx in remaining:
            relevence = query_similarities[chunk_idx]

            selected_embeddings = chunk_embeddings[selected]
            chunk_embedding = chunk_embeddings[chunk_idx]

            similarities_to_selected = (selected_embeddings @ chunk_embedding) / (np.linalg.norm(selected_embeddings,axis=1)*np.linalg.norm(chunk_embedding))
            redundancy = np.max(similarities_to_selected)

            mmr_score = (lambda_mult * relevence) - ( (1- lambda_mult) * redundancy)
            if mmr_score> best_score:
                best_score = mmr_score
                best_index = chunk_idx
        selected.append(best_index)
        remaining.remove(best_index)
    return selected
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


prompt = ChatPromptTemplate.from_messages([
        (
            "system","""
            You are an AI job-hunting assistant.

            Answer the user's question using the provided resume evidence and job information.

            Rules:
            - Ground your answer in the provided resume context.
            - Do not invent skills, experience, projects, achievements, or qualifications that are not supported by the provided context.
            - Use the job description and matching information to understand the requirements of the role.
            - If the resume evidence does not contain enough information to answer the question, clearly say so instead of guessing.
            - When discussing the candidate's suitability, distinguish between skills they have and skills they are missing.
            - Keep the response relevant to the user's question and concise.
            """
        ),
        ('human', "Resume Context:  \n {resume_context} \n\n Company: \n {company} \n role: \n {role} \n Job Description {jd_text} \n Missing skills: \n {missing_skills} \n Matched Skills: \n {matched_skills} \n Match Score: \n {match_score} \n User's Question: {query}")
    ])
struc_llm = llm.with_structured_output(RAGResponse)
chain = prompt | struc_llm
def generate_rag_answer(query: str,retrieved_chunks: list[ResumeChunk],job: Job) -> RAGResponse:
    resume_context = "\n\n".join(chunk.chunk_text for chunk in retrieved_chunks)
    answer = chain.invoke({
        'resume_context': resume_context,
        "company": job.company,
        "role" : job.role,
        "jd_text" : job.jd_text,
        "missing_skills" : job.missing_skills,
        "matched_skills" : job.matched_skills,
        "match_score" : job.match_score,
        "query": query
    })
    return answer

