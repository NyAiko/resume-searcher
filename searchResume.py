from src.vectordb.qdrant_setup import searchForResume
from src.chat.chain import selectTheMostRelevant

def handler(event, context):
    results = searchForResume(event["queryText"])
    resume = selectTheMostRelevant(results, event["queryText"])
    return resume