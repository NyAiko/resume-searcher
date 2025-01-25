import pymupdf
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from src.utils.pdfloader import extractText
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import dotenv
import os

dotenv.load_dotenv()

client = QdrantClient(url = os.getenv("QDRANT_URL"),
                      api_key = os.getenv("QDRANT_API_KEY"))

collection_name = os.getenv("COLLECTION_NAME")

if client.collection_exists(collection_name)==False:
  client.create_collection(collection_name = collection_name,
                           vectors_config=VectorParams(size=768,
                                                       distance=Distance.COSINE)
                            )

embeddings = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY"),
                                          model= "models/text-embedding-004")

def convertTextToEmbeddings(text:str):
  text = extractText(text)
  vector = embeddings.embed_query(text)
  return vector

def storeResume(filepath:str):  
  vector = convertTextToEmbeddings(filepath)
  client.upsert(collection_name=collection_name,
                points=[
                    {"id":str(uuid.uuid4()),
                     "vector":vector,
                     "payload":{"filepath":filepath}
                     }
                
                        ])
  
  return {"Response":200,
          "message": f"The resume **{filepath}** has been processed successfully "}

def searchForResume(textQuery:str):
  vector = embeddings.embed_query(textQuery)
  results = client.query_points(collection_name=collection_name,query=vector,limit=5)
  results = results.points
  resumes = [result.payload.get("filepath") for result in results if result.payload.get("filepath") is not None]

  return resumes
