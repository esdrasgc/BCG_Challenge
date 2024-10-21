import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List

# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

class SemanticChunker:
    def __init__(self, model_name='distilbert-base-uncased', threshold=0.8, batch_size=5, max_tokens=7000):
        # Using the DistilBERT model, which is lighter on memory
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.threshold = threshold
        self.batch_size = batch_size
        self.max_tokens = max_tokens  # Set max tokens based on model's token limit

    def get_embeddings(self, sentences):
        # Truncation to avoid processing very large sequences
        inputs = self.tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Extracting the average of the token representations
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def ensure_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate the input text if it exceeds the token limit."""
        tokens = tokenizer.tokenize(text)
        if len(tokens) > max_tokens:
            # Truncate to the max tokens and convert back to text
            tokens = tokens[:max_tokens]
            return tokenizer.convert_tokens_to_string(tokens)
        return text

    def chunk_text(self, text: str) -> List[str]:
        sentences = text.split('. ')
        chunks = []
        
        # Processing sentences in batches to reduce memory consumption
        for i in range(0, len(sentences), self.batch_size):
            batch_sentences = sentences[i:i+self.batch_size]
            
            # Join batch sentences into one chunk
            current_chunk = ' '.join(batch_sentences)
            
            # Ensure the current chunk is within the token limit
            current_chunk = self.ensure_token_limit(current_chunk, self.max_tokens)
            
            # Tokenize and get embeddings for the current chunk
            chunk_embeddings = self.get_embeddings([current_chunk])

            chunks.append(current_chunk)

        return chunks
