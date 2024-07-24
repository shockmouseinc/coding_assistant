from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def process_content(scraped_data):
    # Combine text and code snippets
    full_text = scraped_data['text'] + ' '.join(scraped_data['code_snippets'])
    
    # Generate embedding
    embedding = model.encode(full_text)
    
    return {
        'url': scraped_data['url'],
        'text': full_text,
        'embedding': embedding
    }