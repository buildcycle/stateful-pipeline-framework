"""Data schemas for document processing pipeline."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Document:
    """Represents a document to be processed."""
    id: str
    content: str
    title: Optional[str] = None


@dataclass
class ClassificationResult:
    """Result of document classification."""
    category: str
    confidence: float


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""
    keywords: List[str]
    scores: List[float]


@dataclass
class Report:
    """Final report generated from processing."""
    document_id: str
    category: str
    keywords: List[str]
    summary: str

