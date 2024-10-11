import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

class SemanticChunker:
    def __init__(self, model_name='distilbert-base-uncased', threshold=0.8, batch_size=5):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.threshold = threshold
        self.batch_size = batch_size

    def get_embeddings(self, sentences):
        inputs = self.tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def chunk_text(self, text):
        sentences = text.split('. ')
        chunks = []
        
        for i in range(0, len(sentences), self.batch_size):
            batch_sentences = sentences[i:i+self.batch_size]
            embeddings = self.get_embeddings(batch_sentences)

            current_chunk = [batch_sentences[0]]
            for j in range(1, len(batch_sentences)):
                similarity = cosine_similarity([embeddings[j-1]], [embeddings[j]])[0][0]
                if similarity < self.threshold:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [batch_sentences[j]]
                else:
                    current_chunk.append(batch_sentences[j])
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))

        return chunks
