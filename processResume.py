from src.vectordb.qdrant_setup import storeResume
from src.utils.aws import getS3uri, rename_s3_object

def handler(event, context):
    s3path = getS3uri(event)
    s3path = rename_s3_object(s3path)
    return storeResume(s3path)
