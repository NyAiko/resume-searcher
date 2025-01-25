from src.vectordb.qdrant_setup import storeResume
from src.utils.aws import getS3uri

def handler(event, context):
    s3path = getS3uri(event)
    return storeResume(s3path)
