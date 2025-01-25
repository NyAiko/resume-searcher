from src.vectordb.qdrant_setup import searchForResume

def handler(event, context):
    return searchForResume(event["queryText"])
