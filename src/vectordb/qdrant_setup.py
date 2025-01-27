from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams,SparseIndexParams,SparseVector
import os
from dotenv import load_dotenv
from src.utils.pdfloader import loadDocument
from typing import List
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
load_dotenv()


collection_name = os.getenv("COLLECTION_NAME")
client = QdrantClient(url = os.getenv("QDRANT_URL"),
                      api_key = os.getenv("QDRANT_API_KEY")
                      )

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25",cache_dir=os.getenv("FASTEMBED_CACHE"))
dense_embeddings = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY"),model= "models/text-embedding-004"
                                                )

if client.collection_exists(collection_name)==False:
  client.create_collection(collection_name=collection_name,
                          vectors_config={"vector":VectorParams(size=768,distance=Distance.COSINE)},
                          sparse_vectors_config = {"sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
                          )

vectorStore = QdrantVectorStore(client=client,
                     collection_name=collection_name,
                     embedding=dense_embeddings,
                     vector_name="vector",
                     sparse_embedding=sparse_embeddings,
                     sparse_vector_name="sparse",
                     retrieval_mode=RetrievalMode.HYBRID,
                    )

def storeResume(filepath:str):
  docs = loadDocument(filepath)
  print("inserting the doc")
  vectorStore.add_documents(
                            documents=docs,
                            #embedding=dense_embeddings,
                            #sparse_embedding= sparse_embeddings,
                            #retrieval_mode=RetrievalMode.HYBRID
                             )
  return {"Response":200,
          "message": f"The file **{filepath}** has been processed successfully "}

def formatSearchResults(results:List[Document]):
  return [{"content":result.page_content, "file_path":result.metadata["source"]} for result in results]

def searchForResume(textQuery:str):
  resumes = vectorStore.similarity_search(query=textQuery)
  resumes = formatSearchResults(resumes)
  return resumes

