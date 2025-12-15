"""Step to classify document text using PyTorch."""

from typing import Dict, Any
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context
from document_processing.schemas import Document, ClassificationResult


class ClassifyTextStep(Step):
    """Classifies document text into categories using PyTorch transformer model."""
    
    def __init__(self):
        super().__init__("classify_text")
        self._model = None
        self._tokenizer = None
        self._categories = ["technical", "business", "legal", "general"]
    
    def _load_model(self):
        """Lazy load the PyTorch model."""
        if self._model is None:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                
                model_name = "distilbert-base-uncased"
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # For demo: use a simple model, in production use fine-tuned model
                # This is a placeholder - you'd train/fine-tune on your categories
                self._model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    num_labels=len(self._categories)
                )
                self._model.eval()
            except Exception as e:
                # Fallback to rule-based if model loading fails
                print(f"Model loading failed, using fallback: {e}")
                return False
        return True
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Classify the document based on content."""
        document = context.get("document")
        if not document:
            raise ValueError("Document not found in context")
        
        if not isinstance(document, Document):
            raise ValueError("Invalid document type in context")
        
        # Try to use PyTorch model, fallback to rule-based
        if self._load_model():
            category, confidence = self._classify_with_model(document.content)
        else:
            category, confidence = self._classify_rule_based(document.content)
        
        classification = ClassificationResult(
            category=category,
            confidence=confidence
        )
        
        return {
            "classification": classification,
            "category": category,
            "confidence": confidence
        }
    
    def _classify_with_model(self, content: str) -> tuple[str, float]:
        """Classify using PyTorch model."""
        try:
            import torch
            
            # Tokenize input
            inputs = self._tokenizer(
                content,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Get prediction
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            category = self._categories[predicted_class % len(self._categories)]
            return category, float(confidence)
        except Exception as e:
            # Fallback to rule-based
            print(f"Model inference failed: {e}, using fallback")
            return self._classify_rule_based(content)
    
    def _classify_rule_based(self, content: str) -> tuple[str, float]:
        """Simple classification logic (fallback)."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["code", "function", "algorithm", "api"]):
            return "technical", 0.85
        elif any(word in content_lower for word in ["revenue", "profit", "market", "sales"]):
            return "business", 0.85
        elif any(word in content_lower for word in ["law", "legal", "contract", "agreement"]):
            return "legal", 0.85
        else:
            return "general", 0.85
