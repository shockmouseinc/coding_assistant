import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sitemap_processor import process_sitemap
from web_scraper import scrape_url
from content_processor import process_content, model as embedding_model
from vector_db import VectorDB
from openai import OpenAI

app = FastAPI()
vector_db = VectorDB()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SitemapInput(BaseModel):
    sitemap_url: str
    user_guidance: list[str]

class Query(BaseModel):
    question: str

@app.post("/process-sitemap")
async def process_sitemap_endpoint(input: SitemapInput):
    urls = process_sitemap(input.sitemap_url, input.user_guidance)
    for url in urls:
        scraped_data = scrape_url(url)
        processed_data = process_content(scraped_data)
        vector_db.add_document(processed_data)
    return {"message": f"Processed {len(urls)} URLs"}

@app.post("/query")
async def query_endpoint(query: Query):
    logging.info(f"Received query: {query.question}")
    
    query_vector = embedding_model.encode(query.question)
    logging.info(f"Encoded query vector shape: {query_vector.shape}")
    
    results = vector_db.search(query_vector, k=3)
    logging.info(f"Search results: {results}")
    
    if not results:
        logging.warning("No results found in the vector database.")
        return {"answer": "I'm sorry, but I couldn't find any relevant information to answer your question.", "source_documents": []}
    
    context = "\n\n".join([doc['content'] for doc in results])
    logging.info(f"Context prepared for LLM: {context[:100]}...")  # Log first 100 chars of context
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query.question}\n\nAnswer:"}
        ]
    )
    
    answer = response.choices[0].message.content
    logging.info(f"LLM response: {answer[:100]}...")  # Log first 100 chars of answer
    
    return {
        "answer": answer,
        "source_documents": [{"url": doc.get('url'), "similarity": doc.get('similarity')} for doc in results]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)