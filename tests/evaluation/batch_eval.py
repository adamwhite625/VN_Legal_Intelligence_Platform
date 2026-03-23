"""
Batch Evaluation - Production Grade

Runs comprehensive evaluation across multiple test cases.
"""

import logging
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from .config import EvaluationConfig
from .metrics import TestCaseResult, EvaluationBatchResult, RetrievalMetrics, AnswerMetrics
from .retrieval_eval import RetrieverEvaluator, RetrieverBenchmark
from .answer_eval import AnswerEvaluator


logger = logging.getLogger(__name__)


class BatchEvaluator:
    """Orchestrates batch evaluation of entire test suite"""
    
    def __init__(self, config: EvaluationConfig):
        """
        Initialize batch evaluator.
        
        Args:
            config: EvaluationConfig instance
        """
        self.config = config
        self.retriever_eval = RetrieverEvaluator(config.retriever)
        self.answer_eval = AnswerEvaluator(config.llm, config.answer)
        self.results: List[TestCaseResult] = []
    
    def set_llm(self, llm: Any) -> None:
        """Set LLM for answer evaluation"""
        self.answer_eval.set_llm(llm)
    
    def evaluate_test_case(
        self,
        test_case: Dict[str, Any],
        retriever: Any,
        answer_generator: Callable
    ) -> TestCaseResult:
        """
        Evaluate a single test case.
        
        Args:
            test_case: Test case dict with question, expected_keywords, etc.
            retriever: Retriever callable
            answer_generator: Function to generate answer from question
            
        Returns:
            TestCaseResult
        """
        test_id = test_case.get("id", "unknown")
        question = test_case.get("question", "")
        
        logger.info(f"Evaluating test: {test_id}")
        start_time = time.time()
        error_message = None
        
        try:
            # Step 1: Retrieve context
            logger.debug("Step 1: Retrieving context...")
            try:
                # Retriever có thể là function hoặc object với .invoke()
                if callable(retriever):
                    # Nếu là function (từ backend_retriever_func)
                    retrieved_chunks = retriever(question)
                else:
                    # Nếu là LangChain retriever object
                    retrieved_chunks = retriever.invoke(question)
                
                if not isinstance(retrieved_chunks, list):
                    retrieved_chunks = [retrieved_chunks]
            except Exception as e:
                logger.error(f"Retrieval failed: {str(e)}")
                retrieved_chunks = []
                error_message = f"Retrieval error: {str(e)}"
            
            # Step 2: Evaluate retrieval
            logger.debug("Step 2: Evaluating retrieval...")
            keywords = test_case.get("expected_keywords", [])
            retrieval_metrics = self.retriever_eval.evaluate_retrieval(
                question, keywords, retrieved_chunks
            )
            
            # Step 3: Generate answer
            logger.debug("Step 3: Generating answer...")
            try:
                generated_answer = answer_generator(question)
            except Exception as e:
                logger.error(f"Answer generation failed: {str(e)}")
                generated_answer = f"Error generating answer: {str(e)}"
                error_message = f"Generation error: {str(e)}"
            
            # Step 4: Evaluate answer
            logger.debug("Step 4: Evaluating answer...")
            reference_answer = test_case.get("reference_answer", "")
            try:
                answer_metrics = self.answer_eval.evaluate_with_llm(
                    question, generated_answer, reference_answer
                )
            except Exception as e:
                logger.error(f"Answer evaluation failed: {str(e)}")
                answer_metrics = AnswerMetrics(
                    accuracy=3.0, completeness=3.0, relevance=3.0,
                    feedback=f"Evaluation error: {str(e)}", is_correct=False
                )
                error_message = error_message or f"Evaluation error: {str(e)}"
            
            # Step 5: Prepare result
            elapsed_time = time.time() - start_time
            
            result = TestCaseResult(
                test_id=test_id,
                question=question,
                category=test_case.get("category", "other"),
                difficulty=test_case.get("difficulty", "medium"),
                generated_answer=generated_answer,
                reference_answer=reference_answer,
                retrieved_context=[
                    {
                        "content": self._get_chunk_content(chunk),
                        "score": self._get_chunk_score(chunk)
                    }
                    for chunk in retrieved_chunks[:self.config.retriever.top_k]
                ],
                retrieval_metrics=retrieval_metrics,
                answer_metrics=answer_metrics,
                execution_time=elapsed_time,
                error_message=error_message
            )
            
            logger.info(
                f"Test {test_id} completed: "
                f"Status={result.status}, Score={answer_metrics.overall_score}/5, "
                f"MRR={retrieval_metrics.mrr:.3f}, Time={elapsed_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error evaluating test {test_id}: {str(e)}", exc_info=True)
            elapsed_time = time.time() - start_time
            
            # Return error result
            return TestCaseResult(
                test_id=test_id,
                question=question,
                category=test_case.get("category", "other"),
                difficulty=test_case.get("difficulty", "medium"),
                generated_answer="",
                reference_answer=test_case.get("reference_answer", ""),
                retrieved_context=[],
                retrieval_metrics=RetrievalMetrics(
                    mrr=0.0, ndcg=0.0, keyword_coverage=0.0,
                    keywords_found=0, total_keywords=0, docs_retrieved=0,
                    avg_relevance_score=0.0
                ),
                answer_metrics=AnswerMetrics(
                    accuracy=1.0, completeness=1.0, relevance=1.0,
                    feedback=f"System error: {str(e)}", is_correct=False
                ),
                execution_time=elapsed_time,
                error_message=str(e)
            )
    
    def run_evaluation(
        self,
        test_cases: List[Dict[str, Any]],
        retriever: Any,
        answer_generator: Callable,
        batch_id: Optional[str] = None
    ) -> EvaluationBatchResult:
        """
        Run evaluation on all test cases.
        
        Args:
            test_cases: List of test case dicts
            retriever: Retriever callable
            answer_generator: Answer generation function
            batch_id: Optional batch ID
            
        Returns:
            EvaluationBatchResult
        """
        if batch_id is None:
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Starting batch evaluation: {batch_id}")
        logger.info(f"Total tests: {len(test_cases)}")
        
        start_time = datetime.utcnow()
        wall_start = time.time()
        
        # Run evaluation on each test case
        self.results = []
        for i, test_case in enumerate(test_cases, 1):
            if self.config.batch.verbose:
                logger.info(f"[{i}/{len(test_cases)}] {test_case.get('id', 'unknown')}")
            
            result = self.evaluate_test_case(test_case, retriever, answer_generator)
            self.results.append(result)
            
            # Save intermediate results if configured
            if self.config.batch.save_intermediate_results:
                self._persist_intermediate_result(batch_id, result)
        
        # Aggregate results
        end_time = datetime.utcnow()
        wall_end = time.time()
        
        batch_result = self._aggregate_results(
            batch_id, self.results, start_time, end_time, wall_end - wall_start
        )
        
        logger.info(f"Batch evaluation completed: {batch_id}")
        logger.info(f"Success rate: {batch_result.success_rate}%")
        logger.info(f"Average score: {batch_result.avg_overall_score:.2f}/5")
        
        return batch_result
    
    def _aggregate_results(
        self,
        batch_id: str,
        results: List[TestCaseResult],
        start_time: datetime,
        end_time: datetime,
        duration: float
    ) -> EvaluationBatchResult:
        """Aggregate individual results into batch result"""
        
        # Count statuses
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        errors = sum(1 for r in results if r.status == "ERROR")
        
        # Aggregate metrics
        retrieval_results = [r.retrieval_metrics for r in results if r.error_message is None]
        answer_results = [r.answer_metrics for r in results if r.error_message is None]
        
        avg_mrr = (
            sum(r.mrr for r in retrieval_results) / len(retrieval_results)
            if retrieval_results else 0.0
        )
        avg_ndcg = (
            sum(r.ndcg for r in retrieval_results) / len(retrieval_results)
            if retrieval_results else 0.0
        )
        avg_coverage = (
            sum(r.keyword_coverage for r in retrieval_results) / len(retrieval_results)
            if retrieval_results else 0.0
        )
        
        avg_accuracy = (
            sum(r.accuracy for r in answer_results) / len(answer_results)
            if answer_results else 0.0
        )
        avg_completeness = (
            sum(r.completeness for r in answer_results) / len(answer_results)
            if answer_results else 0.0
        )
        avg_relevance = (
            sum(r.relevance for r in answer_results) / len(answer_results)
            if answer_results else 0.0
        )
        
        # Calculate weighted overall score
        avg_overall = (
            avg_accuracy * 0.4 +
            avg_completeness * 0.3 +
            avg_relevance * 0.3
        )
        
        # Category breakdown
        category_results = self._breakdown_by_category(results)
        
        # Quality gates check (both retrieval quality and answer quality)
        quality_gates_passed = self._check_quality_gates(avg_mrr, avg_ndcg, avg_accuracy)
        
        batch_result = EvaluationBatchResult(
            batch_id=batch_id,
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            error_tests=errors,
            avg_mrr=round(avg_mrr, 3),
            avg_ndcg=round(avg_ndcg, 3),
            avg_keyword_coverage=round(avg_coverage, 3),
            avg_accuracy=round(avg_accuracy, 2),
            avg_completeness=round(avg_completeness, 2),
            avg_relevance=round(avg_relevance, 2),
            avg_overall_score=round(avg_overall, 2),
            category_results=category_results,
            quality_gates_passed=quality_gates_passed,
            test_results=results,
            start_time=start_time,
            end_time=end_time,
            duration=round(duration, 2)
        )
        
        return batch_result
    
    def _breakdown_by_category(self, results: List[TestCaseResult]) -> Dict[str, Dict[str, float]]:
        """Break down results by category"""
        from collections import defaultdict
        
        category_data = defaultdict(lambda: {"retrieval": [], "answers": []})
        
        for result in results:
            if result.error_message is None:
                cat = result.category
                category_data[cat]["retrieval"].append(result.retrieval_metrics)
                category_data[cat]["answers"].append(result.answer_metrics)
        
        category_results = {}
        for category, data in category_data.items():
            n_ret = len(data["retrieval"])
            n_ans = len(data["answers"])
            
            if n_ret > 0 and n_ans > 0:
                avg_mrr = sum(r.mrr for r in data["retrieval"]) / n_ret
                avg_acc = sum(r.accuracy for r in data["answers"]) / n_ans
                errors = sum(1 for r in data["answers"] if not r.is_correct)
                
                category_results[category] = {
                    "mrr": round(avg_mrr, 3),
                    "accuracy": round(avg_acc, 2),
                    "count": len(data["answers"]),
                    "errors": errors
                }
        
        return category_results
    
    def _check_quality_gates(self, avg_mrr: float, avg_ndcg: float, avg_accuracy: float) -> bool:
        """Check production quality gates - realistic thresholds"""
        config = self.config.quality_gates
        
        # Both retrieval and answer quality must meet thresholds
        # Retrieval: either MRR or nDCG must pass (allowing flexibility)
        retrieval_ok = (avg_mrr >= config.min_retrieval_mrr) or (avg_ndcg >= config.min_retrieval_ndcg)
        answer_ok = avg_accuracy >= config.min_answer_accuracy
        
        passed = retrieval_ok and answer_ok
        return passed
    
    def _persist_intermediate_result(self, batch_id: str, result: TestCaseResult) -> None:
        """Save intermediate result to storage"""
        try:
            output_dir = Path(self.config.reporting.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            result_file = output_dir / f"{batch_id}_intermediate.jsonl"
            with open(result_file, "a", encoding='utf-8') as f:
                f.write(result.model_dump_json() + "\n")
        except Exception as e:
            logger.warning(f"Failed to persist intermediate result: {str(e)}")
    
    def _get_chunk_content(self, chunk: Any) -> str:
        """Extract content from chunk"""
        if isinstance(chunk, dict):
            return chunk.get("page_content", chunk.get("content", str(chunk)))
        elif hasattr(chunk, "page_content"):
            return chunk.page_content
        elif hasattr(chunk, "content"):
            return chunk.content
        else:
            return str(chunk)[:200]
    
    def _get_chunk_score(self, chunk: Any) -> float:
        """Extract score from chunk"""
        if isinstance(chunk, dict) and "score" in chunk:
            return chunk["score"]
        elif hasattr(chunk, "metadata") and isinstance(chunk.metadata, dict):
            return chunk.metadata.get("score", 0.5)
        return 0.5
