"""Step to extract keywords from document using PyTorch."""

from typing import Dict, Any, List
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context
from document_processing.schemas import Document, KeywordExtractionResult


class ExtractKeywordsStep(Step):
    """Extracts keywords from document content using PyTorch NLP models."""
    
    def __init__(self, max_keywords: int = 5):
        super().__init__("extract_keywords")
        self.max_keywords = max_keywords
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """Lazy load the PyTorch model."""
        if self._model is None:
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._model = AutoModel.from_pretrained(model_name)
                self._model.eval()
            except Exception as e:
                print(f"Model loading failed, using fallback: {e}")
                return False
        return True
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Extract keywords from the document."""
        document = context.get("document")
        if not document:
            raise ValueError("Document not found in context")
        
        if not isinstance(document, Document):
            raise ValueError("Invalid document type in context")
        
        # Try to use PyTorch model, fallback to frequency-based
        if self._load_model():
            keywords_result = self._extract_keywords_with_model(document.content)
        else:
            keywords_result = self._extract_keywords_frequency(document.content)
        
        return {
            "keywords": keywords_result.keywords,
            "keyword_scores": keywords_result.scores,
            "keyword_extraction": keywords_result
        }
    
    def _extract_keywords_with_model(self, content: str) -> KeywordExtractionResult:
        """Extract keywords using PyTorch model."""
        try:
            import torch
            import numpy as np
            from collections import Counter
            
            # Tokenize and get embeddings
            inputs = self._tokenizer(
                content,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                # Use mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # For demo: extract important tokens
            # In production, use proper keyword extraction models
            tokens = self._tokenizer.tokenize(content)
            word_freq = Counter(tokens)
            
            # Filter and rank
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
            filtered = [(word, freq) for word, freq in word_freq.items() 
                       if word.lower() not in stop_words and len(word) > 3]
            sorted_words = sorted(filtered, key=lambda x: x[1], reverse=True)
            
            top_keywords = [word for word, _ in sorted_words[:self.max_keywords]]
            scores = [freq / len(tokens) for _, freq in sorted_words[:self.max_keywords]]
            
            return KeywordExtractionResult(
                keywords=top_keywords,
                scores=scores
            )
        except Exception as e:
            print(f"Model inference failed: {e}, using fallback")
            return self._extract_keywords_frequency(content)
    
    def _extract_keywords_frequency(self, content: str) -> KeywordExtractionResult:
        """Simple keyword extraction logic (fallback)."""
        words = content.lower().split()
        
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, _ in sorted_words[:self.max_keywords]]
        scores = [freq / len(filtered_words) for _, freq in sorted_words[:self.max_keywords]]
        
        return KeywordExtractionResult(
            keywords=top_keywords,
            scores=scores
        )
