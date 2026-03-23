"""
Answer Quality Evaluation - Production Grade

Evaluates generated answers using LLM-as-a-judge or manual scoring.
"""

import logging
import json
import re
from typing import Optional, Tuple, List, Any
from .config import LLMConfig, AnswerEvaluationConfig
from .metrics import AnswerMetrics


logger = logging.getLogger(__name__)


class AnswerEvaluator:
    """Evaluates answer quality"""
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        answer_config: Optional[AnswerEvaluationConfig] = None
    ):
        """
        Initialize answer evaluator.
        
        Args:
            llm_config: LLM configuration
            answer_config: Answer evaluation configuration
        """
        self.llm_config = llm_config or LLMConfig()
        self.answer_config = answer_config or AnswerEvaluationConfig()
        self.llm = None
    
    def set_llm(self, llm: Any) -> None:
        """
        Set the LLM instance for evaluation.
        
        Args:
            llm: LLM instance (e.g., ChatOpenAI, Ollama)
        """
        self.llm = llm
        logger.info(f"LLM set to {self.llm_config.model_name}")
    
    def evaluate_with_llm(
        self,
        question: str,
        generated_answer: str,
        reference_answer: str
    ) -> AnswerMetrics:
        """
        Automated evaluation using LLM-as-a-judge.
        
        The LLM compares answer against reference.
        
        Args:
            question: The question asked
            generated_answer: System-generated answer
            reference_answer: Expected correct answer
            
        Returns:
            AnswerMetrics with LLM evaluation
        """
        if self.llm is None:
            raise ValueError("LLM not set. Call set_llm() first.")
        
        logger.info(f"Evaluating answer with LLM: {self.llm_config.model_name}")
        
        # Create evaluation prompt
        judge_prompt = self._create_judge_prompt(
            question, generated_answer, reference_answer
        )
        
        try:
            # Get LLM evaluation
            response = self.llm.invoke(judge_prompt)
            response_text = self._extract_response(response)
            
            # Parse scores from response
            scores = self._parse_scores(response_text)
            
            # Extract feedback
            feedback = self._extract_feedback(response_text)
            
            metrics = AnswerMetrics(
                accuracy=scores.get("accuracy", 3.0),
                completeness=scores.get("completeness", 3.0),
                relevance=scores.get("relevance", 3.0),
                feedback=feedback,
                is_correct=(
                    scores.get("accuracy", 0) >= 4.0 and
                    scores.get("relevance", 0) >= 4.0
                )
            )
            
            logger.info(f"LLM evaluation result: {metrics.overall_score}/5")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during LLM evaluation: {str(e)}")
            # Return neutral scores on error
            return AnswerMetrics(
                accuracy=3.0,
                completeness=3.0,
                relevance=3.0,
                feedback=f"Evaluation error: {str(e)}",
                is_correct=False
            )
    
    def evaluate_manually(
        self,
        question: str,
        generated_answer: str,
        reference_answer: str,
        accuracy: float,
        completeness: float,
        relevance: float,
        feedback: str = ""
    ) -> AnswerMetrics:
        """
        Manual evaluation by human rater.
        
        Args:
            question: The question
            generated_answer: System answer
            reference_answer: Reference answer
            accuracy: Accuracy score (1-5)
            completeness: Completeness score (1-5)
            relevance: Relevance score (1-5)
            feedback: Human feedback
            
        Returns:
            AnswerMetrics with manual scores
        """
        logger.info("Creating manually-scored AnswerMetrics")
        
        metrics = AnswerMetrics(
            accuracy=float(accuracy),
            completeness=float(completeness),
            relevance=float(relevance),
            feedback=feedback or "Manually evaluated",
            is_correct=(
                accuracy >= self.answer_config.min_accuracy_threshold and
                relevance >= self.answer_config.min_relevance_threshold
            )
        )
        
        return metrics
    
    def check_quality_gates(self, metrics: AnswerMetrics) -> Tuple[bool, List[str]]:
        """
        Check if answer meets quality standards.
        
        Args:
            metrics: AnswerMetrics to check
            
        Returns:
            Tuple of (passed: bool, failed_checks: List[str])
        """
        failed_checks = []
        config = self.answer_config
        
        if metrics.accuracy < config.min_accuracy_threshold:
            failed_checks.append(
                f"Accuracy {metrics.accuracy:.1f} < {config.min_accuracy_threshold}"
            )
        
        if metrics.completeness < config.min_completeness_threshold:
            failed_checks.append(
                f"Completeness {metrics.completeness:.1f} < "
                f"{config.min_completeness_threshold}"
            )
        
        if metrics.relevance < config.min_relevance_threshold:
            failed_checks.append(
                f"Relevance {metrics.relevance:.1f} < {config.min_relevance_threshold}"
            )
        
        passed = len(failed_checks) == 0
        
        logger.info(
            f"Answer quality gate check: {'PASSED' if passed else 'FAILED'}"
        )
        
        return passed, failed_checks
    
    def _create_judge_prompt(
        self,
        question: str,
        generated_answer: str,
        reference_answer: str
    ) -> str:
        """Create the prompt for LLM-as-judge"""
        prompt = f"""You are an expert evaluator for a Legal Chatbot specializing in Korean legal matters.

Your task is to evaluate the quality of a generated answer compared to a reference answer.

QUESTION:
{question}

REFERENCE ANSWER (Expected correct answer):
{reference_answer}

GENERATED ANSWER (To be evaluated):
{generated_answer}

Please evaluate the generated answer on these THREE dimensions using a scale of 1-5:

**1. ACCURACY** - Is the information factually correct and based on valid legal knowledge?
   - 5: All facts are absolutely correct and precise
   - 4: Mostly correct with very minor inaccuracies
   - 3: Contains some factual errors but main point is correct
   - 2: Multiple factual errors, misleading
   - 1: Seriously wrong or contains false information

**2. COMPLETENESS** - Does it cover all important aspects from the reference answer?
   - 5: Covers all key information comprehensively
   - 4: Covers most key information, minor details missing
   - 3: Covers main points but significant details missing
   - 2: Missing important information
   - 1: Very incomplete, major gaps

**3. RELEVANCE** - Does it directly address the specific question asked?
   - 5: Perfect focus, completely on-topic, no unnecessary information
   - 4: Mostly on-topic, minor extraneous content
   - 3: Addresses question but includes some irrelevant info
   - 2: Partially off-topic or includes significant irrelevant content
   - 1: Off-topic or fails to address question

You MUST respond in this exact format, with no additional text:

ACCURACY: [1-5]
COMPLETENESS: [1-5]
RELEVANCE: [1-5]
FEEDBACK: [2-3 sentence explanation of your evaluation]

Be strict but fair. This is for production use."""
        
        return prompt
    
    def _extract_response(self, response: Any) -> str:
        """Extract text from LLM response (handles different formats)"""
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, dict) and "content" in response:
            return response["content"]
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def _parse_scores(self, response_text: str) -> dict:
        """Parse accuracy, completeness, relevance scores from response"""
        scores = {}
        
        # Look for ACCURACY score
        accuracy_match = re.search(r"ACCURACY:\s*(\d+(?:\.\d+)?)", response_text)
        if accuracy_match:
            score = float(accuracy_match.group(1))
            scores["accuracy"] = min(5.0, max(1.0, score))
        
        # Look for COMPLETENESS score
        completeness_match = re.search(r"COMPLETENESS:\s*(\d+(?:\.\d+)?)", response_text)
        if completeness_match:
            score = float(completeness_match.group(1))
            scores["completeness"] = min(5.0, max(1.0, score))
        
        # Look for RELEVANCE score
        relevance_match = re.search(r"RELEVANCE:\s*(\d+(?:\.\d+)?)", response_text)
        if relevance_match:
            score = float(relevance_match.group(1))
            scores["relevance"] = min(5.0, max(1.0, score))
        
        logger.debug(f"Parsed scores: {scores}")
        return scores
    
    def _extract_feedback(self, response_text: str) -> str:
        """Extract feedback from response"""
        # Look for FEEDBACK section
        feedback_match = re.search(
            r"FEEDBACK:\s*(.+?)(?:\n|$)", response_text, re.DOTALL
        )
        
        if feedback_match:
            feedback = feedback_match.group(1).strip()
            # Limit to reasonable length
            if len(feedback) > 500:
                feedback = feedback[:497] + "..."
            return feedback
        
        return "No feedback provided"


class BatchAnswerEvaluator:
    """Batch evaluation of multiple answers"""
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        answer_config: Optional[AnswerEvaluationConfig] = None
    ):
        self.evaluator = AnswerEvaluator(llm_config, answer_config)
    
    def evaluate_batch(
        self,
        test_cases: List[dict],
        use_manual_scores: bool = False
    ) -> List[AnswerMetrics]:
        """
        Evaluate multiple test cases.
        
        Args:
            test_cases: List of test case dicts with question, answer, reference_answer
            use_manual_scores: If True, use manual scores from test_cases
            
        Returns:
            List of AnswerMetrics
        """
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Evaluating answer {i}/{len(test_cases)}")
            
            try:
                if use_manual_scores and "scores" in test_case:
                    metrics = self.evaluator.evaluate_manually(
                        test_case.get("question", ""),
                        test_case.get("generated_answer", ""),
                        test_case.get("reference_answer", ""),
                        test_case["scores"].get("accuracy", 3.0),
                        test_case["scores"].get("completeness", 3.0),
                        test_case["scores"].get("relevance", 3.0),
                        test_case.get("feedback", "")
                    )
                else:
                    metrics = self.evaluator.evaluate_with_llm(
                        test_case.get("question", ""),
                        test_case.get("generated_answer", ""),
                        test_case.get("reference_answer", "")
                    )
                
                results.append(metrics)
                
            except Exception as e:
                logger.error(f"Error evaluating test case {i}: {str(e)}")
                # Add neutral metric on error
                results.append(
                    AnswerMetrics(
                        accuracy=3.0,
                        completeness=3.0,
                        relevance=3.0,
                        feedback=f"Evaluation failed: {str(e)}",
                        is_correct=False
                    )
                )
        
        return results
