"""
Retrieval Evaluation - Production Grade

Evaluates retrieval quality using MRR, nDCG, and keyword coverage.
"""

import math
import logging
from typing import List, Tuple, Optional, Any
from .config import RetrieverConfig
from .metrics import RetrievalMetrics


logger = logging.getLogger(__name__)


class RetrieverEvaluator:
    """Evaluates retrieval system quality"""
    
    def __init__(self, config: Optional[RetrieverConfig] = None):
        """
        Initialize retriever evaluator.
        
        Args:
            config: RetrieverConfig instance
        """
        self.config = config or RetrieverConfig()
    
    def calculate_mrr(
        self,
        keyword: str,
        retrieved_chunks: List[Any]
    ) -> float:
        """
        Calculate Mean Reciprocal Rank for a keyword.
        
        MRR = 1 / rank_of_first_relevant_doc
        - If keyword in 1st doc: MRR = 1.0
        - If keyword in 3rd doc: MRR = 0.333
        - If not found: MRR = 0.0
        
        Args:
            keyword: Keyword to search for
            retrieved_chunks: List of retrieved chunks
            
        Returns:
            MRR score (0.0 to 1.0)
        """
        keyword_lower = keyword.lower()
        
        for rank, chunk in enumerate(retrieved_chunks, start=1):
            # Get chunk content
            content = self._get_chunk_content(chunk)
            
            if keyword_lower in content.lower():
                mrr = 1.0 / rank
                logger.debug(f"Found '{keyword}' at rank {rank}, MRR={mrr:.3f}")
                return mrr
        
        logger.debug(f"Keyword '{keyword}' not found in retrieved chunks")
        return 0.0
    
    def calculate_dcg(self, relevances: List[int], k: int) -> float:
        """
        Calculate Discounted Cumulative Gain.
        
        DCG = Σ (relevance_i / log2(i + 1))
        
        Args:
            relevances: List of relevance scores (binary: 1 or 0)
            k: Number of positions to consider
            
        Returns:
            DCG score
        """
        dcg = 0.0
        for i in range(min(k, len(relevances))):
            # i+2 because: rank starts at 1, log2(1)=0
            dcg += relevances[i] / math.log2(i + 2)
        
        logger.debug(f"Calculated DCG={dcg:.3f} for k={k}")
        return dcg
    
    def calculate_ndcg(
        self,
        keyword: str,
        retrieved_chunks: List[Any],
        k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain.
        
        nDCG = DCG / IDCG
        - Perfect ranking: nDCG = 1.0
        - Keyword not found: nDCG = 0.0
        
        Args:
            keyword: Keyword to evaluate
            retrieved_chunks: List of retrieved chunks
            k: Number of top chunks to consider
            
        Returns:
            nDCG score (0.0 to 1.0)
        """
        keyword_lower = keyword.lower()
        
        # Calculate binary relevance scores
        relevances = []
        for chunk in retrieved_chunks[:k]:
            content = self._get_chunk_content(chunk)
            
            if keyword_lower in content.lower():
                relevances.append(1)
            else:
                relevances.append(0)
        
        # Calculate actual DCG
        dcg = self.calculate_dcg(relevances, k)
        
        # Calculate ideal DCG (best case: all relevant at top)
        ideal_relevances = sorted(relevances, reverse=True)
        idcg = self.calculate_dcg(ideal_relevances, k)
        
        # Normalize
        if idcg > 0:
            ndcg = dcg / idcg
        else:
            ndcg = 0.0
        
        logger.debug(f"Calculated nDCG={ndcg:.3f} for keyword '{keyword}'")
        return ndcg
    
    def evaluate_keywords(
        self,
        keywords: List[str],
        retrieved_chunks: List[Any]
    ) -> Tuple[float, float, int, float]:
        """
        Evaluate multiple keywords and get aggregated metrics.
        
        Args:
            keywords: List of keywords to find
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Tuple of (avg_mrr, avg_ndcg, keywords_found, coverage_percent)
        """
        if not keywords or not retrieved_chunks:
            return 0.0, 0.0, 0, 0.0
        
        mrr_scores = []
        ndcg_scores = []
        
        for keyword in keywords:
            mrr = self.calculate_mrr(keyword, retrieved_chunks)
            ndcg = self.calculate_ndcg(keyword, retrieved_chunks, k=len(retrieved_chunks))
            
            mrr_scores.append(mrr)
            ndcg_scores.append(ndcg)
        
        # Calculate averages
        avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0
        avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
        
        # Calculate coverage
        keywords_found = sum(1 for score in mrr_scores if score > 0)
        coverage = (keywords_found / len(keywords) * 100) if keywords else 0.0
        
        logger.info(
            f"Keyword evaluation: "
            f"MRR={avg_mrr:.3f}, nDCG={avg_ndcg:.3f}, "
            f"Coverage={coverage:.1f}% ({keywords_found}/{len(keywords)})"
        )
        
        return avg_mrr, avg_ndcg, keywords_found, coverage
    
    def evaluate_retrieval(
        self,
        question: str,
        keywords: List[str],
        retrieved_chunks: List[Any]
    ) -> RetrievalMetrics:
        """
        Comprehensive retrieval evaluation.
        
        Args:
            question: Original question
            keywords: Expected keywords
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            RetrievalMetrics object
        """
        logger.info(f"Evaluating retrieval for question: {question[:50]}...")
        
        # Evaluate keywords
        avg_mrr, avg_ndcg, keywords_found, coverage = self.evaluate_keywords(
            keywords,
            retrieved_chunks
        )
        
        # Calculate average relevance score if available
        avg_relevance_score = self._calculate_avg_relevance(
            retrieved_chunks
        )
        
        metrics = RetrievalMetrics(
            mrr=avg_mrr,
            ndcg=avg_ndcg,
            keyword_coverage=coverage,
            keywords_found=keywords_found,
            total_keywords=len(keywords),
            docs_retrieved=len(retrieved_chunks),
            avg_relevance_score=avg_relevance_score
        )
        
        logger.debug(f"Retrieval metrics: {metrics}")
        return metrics
    
    def _get_chunk_content(self, chunk: Any) -> str:
        """Extract text content from chunk (handles different formats)"""
        if isinstance(chunk, dict):
            return chunk.get("page_content", chunk.get("content", str(chunk)))
        elif hasattr(chunk, "page_content"):
            return chunk.page_content
        elif hasattr(chunk, "content"):
            return chunk.content
        else:
            return str(chunk)
    
    def _calculate_avg_relevance(self, chunks: List[Any]) -> float:
        """Calculate average relevance score from chunks"""
        if not chunks:
            return 0.0
        
        scores = []
        for chunk in chunks:
            if isinstance(chunk, dict) and "score" in chunk:
                scores.append(chunk["score"])
            elif hasattr(chunk, "metadata") and "score" in chunk.metadata:
                scores.append(chunk.metadata["score"])
        
        if scores:
            avg = sum(scores) / len(scores)
            return round(avg, 3)
        
        return 0.5  # Default neutral score


class RetrieverBenchmark:
    """Benchmark retriever against known good results"""
    
    def __init__(self, config: Optional[RetrieverConfig] = None):
        self.evaluator = RetrieverEvaluator(config)
        self.config = config or RetrieverConfig()
    
    def check_quality_gates(self, metrics: RetrievalMetrics) -> Tuple[bool, List[str]]:
        """
        Check if metrics meet production standards.
        
        Args:
            metrics: RetrievalMetrics to check
            
        Returns:
            Tuple of (passed: bool, failed_checks: List[str])
        """
        failed_checks = []
        
        if metrics.mrr < self.config.min_mrr_threshold:
            failed_checks.append(
                f"MRR {metrics.mrr:.3f} < threshold {self.config.min_mrr_threshold}"
            )
        
        if metrics.ndcg < self.config.min_ndcg_threshold:
            failed_checks.append(
                f"nDCG {metrics.ndcg:.3f} < threshold {self.config.min_ndcg_threshold}"
            )
        
        if metrics.keyword_coverage < self.config.min_coverage_threshold:
            failed_checks.append(
                f"Coverage {metrics.keyword_coverage:.1f}% < "
                f"threshold {self.config.min_coverage_threshold:.1f}%"
            )
        
        passed = len(failed_checks) == 0
        
        logger.info(
            f"Quality gate check: {'PASSED' if passed else 'FAILED'}"
        )
        if failed_checks:
            for check in failed_checks:
                logger.warning(f"  ✗ {check}")
        
        return passed, failed_checks
