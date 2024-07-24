import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class VectorDB:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_PROJECT_URL")
        key: str = os.environ.get("SUPABASE_PUBLIC_KEY")
        self.supabase: Client = create_client(url, key)

    def add_document(self, document):
        self.supabase.table('documents').insert({
            'url': document['url'],
            'content': document['text'],
            'embedding': document['embedding'].tolist()
        }).execute()

    def search(self, query_vector, k=5):
        query_embedding = np.array(query_vector).tolist()
        result = self.supabase.rpc(
            'match_documents', 
            {'query_embedding': query_embedding, 'match_threshold': 0.0, 'match_count': k}
        ).execute()
        
        logging.info(f"Search result: {result}")
        logging.info(f"Search data: {result.data}")
        
        return result.data if result.data else []