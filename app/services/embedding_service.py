from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.models.resume import Resume
from app.models.resume_chunk import ResumeChunk
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")
splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

def generate_resume_embeddings(resume : Resume,db: Session ):
    chunks = splitter.split_text(resume.raw_text)
    embeddings = embedding_model.embed_documents(chunks)
    #delte old resume chunk 
    db.query(ResumeChunk).filter(ResumeChunk.resume_id == resume.id).delete()

    #create new resume chunk object
    for chunk,embed in zip(chunks,embeddings):
        new_resume_chunk = ResumeChunk(
            resume_id =  resume.id,
            chunk_text =  chunk,
            embedding = embed,
            resume_updated_at=resume.updated_at
        )
        db.add(new_resume_chunk)
    
    db.commit()
 
    return{"message":"Embeddings generated successfully."}
