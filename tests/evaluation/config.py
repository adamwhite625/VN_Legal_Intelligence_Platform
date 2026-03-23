"""
Evaluation Configuration - Production Grade

Centralized configuration for all evaluation parameters.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Difficulty(Enum):
    """Test case difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(Enum):
    """Question categories for legal chatbot"""
    ADMISSION = "admission"
    VISA = "visa"
    TUITION = "tuition"
    LIVING = "living"
    CAMPUS_LIFE = "campus_life"
    OTHER = "other"


@dataclass
class RetrieverConfig:
    """Configuration for retrieval evaluation"""
    
    # Retrieval parameters
    top_k: int = 5
    min_similarity_score: float = 0.6
    embed_model: str = "text-embedding-3-small"
    
    # Evaluation thresholds (for production checks)
    min_mrr_threshold: float = 0.7
    min_ndcg_threshold: float = 0.75
    min_coverage_threshold: float = 0.90
    
    # Timeout settings
    query_timeout: int = 30  # seconds
    batch_timeout: int = 300  # seconds


@dataclass
class LLMConfig:
    """Configuration for LLM-based evaluation"""
    
    # Model settings
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 500
    
    # Evaluation settings
    use_local_model: bool = False
    local_model_name: Optional[str] = None  # e.g., "ollama/mistral"
    
    # Timeout settings
    response_timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: int = 2  # seconds


@dataclass
class AnswerEvaluationConfig:
    """Configuration for answer quality evaluation"""
    
    # Scoring criteria (scale 1-5)
    max_score: float = 5.0
    min_score: float = 1.0
    
    # Thresholds for production
    min_accuracy_threshold: float = 4.5
    min_completeness_threshold: float = 4.3
    min_relevance_threshold: float = 4.5
    
    # Evaluation method
    use_llm_judge: bool = True
    manual_review_sample_size: int = 0.1  # 10% for manual review
    
    # Scoring rubric
    accuracy_weight: float = 0.4
    completeness_weight: float = 0.3
    relevance_weight: float = 0.3


@dataclass
class BatchEvaluationConfig:
    """Configuration for batch evaluation"""
    
    # Batch settings
    batch_size: int = 10
    parallel_workers: int = 3
    
    # Test selection
    test_categories: List[str] = field(
        default_factory=lambda: [
            "admission", "visa", "tuition", "living", "campus_life"
        ]
    )
    test_difficulties: List[str] = field(
        default_factory=lambda: ["easy", "medium", "hard"]
    )
    
    # Filtering
    only_high_priority: bool = False
    sample_size: Optional[int] = None  # None = all tests
    
    # Logging
    verbose: bool = True
    log_failed_cases: bool = True
    save_intermediate_results: bool = True


@dataclass
class QualityGatesConfig:
    """Configuration for production quality gates"""
    
    # Checks before deployment
    checks_enabled: bool = True
    
    # Metric thresholds (realistic for V1 baseline)
    min_retrieval_mrr: float = 0.62  # Adjusted to realistic level
    min_retrieval_ndcg: float = 0.62  # Adjusted to realistic level
    min_answer_accuracy: float = 4.4  # Slightly relaxed
    min_faithfulness: float = 0.85
    
    # Regression thresholds (compared to baseline)
    max_metric_regression: float = 0.05  # 5% regression allowed
    max_error_rate_increase: float = 0.02  # 2% error rate increase
    
    # Category-specific thresholds
    category_regression_threshold: float = 0.1  # 10% per category
    
    # Failure handling
    allow_deployment_on_failure: bool = False
    notify_on_failure: bool = True


@dataclass
class ReportingConfig:
    """Configuration for report generation"""
    
    # Report generation
    generate_html: bool = True
    generate_excel: bool = True
    generate_json: bool = True
    generate_csv: bool = True
    
    # Report details
    include_category_breakdown: bool = True
    include_error_analysis: bool = True
    include_trend_analysis: bool = True
    include_recommendations: bool = True
    
    # Output paths
    output_dir: str = "tests/results/reports"
    artifact_dir: str = "tests/results/artifacts"
    
    # Versioning
    include_git_hash: bool = True
    include_timestamp: bool = True
    
    # Thresholds for highlighting
    warn_threshold_mrr: float = 0.65
    warn_threshold_accuracy: float = 4.0
    critical_threshold_mrr: float = 0.5
    critical_threshold_accuracy: float = 3.5


@dataclass
class EvaluationConfig:
    """Main evaluation configuration - aggregates all configs"""
    
    # Sub-configurations
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    answer: AnswerEvaluationConfig = field(default_factory=AnswerEvaluationConfig)
    batch: BatchEvaluationConfig = field(default_factory=BatchEvaluationConfig)
    quality_gates: QualityGatesConfig = field(default_factory=QualityGatesConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    
    # Global settings
    random_seed: int = 42
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # Database/Storage
    results_db_path: str = "tests/results/evaluation_results.db"
    baseline_file: str = "tests/results/baseline.json"
    
    @classmethod
    def development(cls) -> "EvaluationConfig":
        """Development configuration - relaxed thresholds"""
        config = cls()
        config.retriever.top_k = 5
        config.retriever.min_mrr_threshold = 0.5
        config.retriever.min_ndcg_threshold = 0.5
        config.answer.min_accuracy_threshold = 3.5
        config.batch.batch_size = 5
        return config
    
    @classmethod
    def staging(cls) -> "EvaluationConfig":
        """Staging configuration - intermediate thresholds"""
        config = cls()
        config.retriever.top_k = 10
        config.retriever.min_mrr_threshold = 0.65
        config.retriever.min_ndcg_threshold = 0.7
        config.answer.min_accuracy_threshold = 4.0
        config.batch.batch_size = 10
        return config
    
    @classmethod
    def production(cls) -> "EvaluationConfig":
        """Production configuration - strict thresholds"""
        config = cls()
        config.retriever.top_k = 15
        # Default is already strict, but can be overridden
        config.quality_gates.allow_deployment_on_failure = False
        config.quality_gates.notify_on_failure = True
        return config


# Default configurations
DEFAULT_CONFIG = EvaluationConfig()
DEV_CONFIG = EvaluationConfig.development()
STAGING_CONFIG = EvaluationConfig.staging()
PROD_CONFIG = EvaluationConfig.production()
