#!/usr/bin/env python3
"""
Production-grade RAG evaluation cho Legal Chatbot.

Usage:
    python RUN_EVALUATION.py --config dev --sample 5
    python RUN_EVALUATION.py --config staging
    python RUN_EVALUATION.py --config prod
"""

import sys
import os
import json
import logging
import argparse
import httpx
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from tests.evaluation.config import DEV_CONFIG, STAGING_CONFIG, PROD_CONFIG
from tests.evaluation.batch_eval import BatchEvaluator
from tests.evaluation.reporting import ReportGenerator
from tests.evaluation.utils import TestDatasetManager
from app.core.config import settings
from langchain_openai import ChatOpenAI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SEARCH_ENDPOINT = f"{BACKEND_URL}/api/v1/search/search"

# ============================================
# BACKEND RETRIEVER (gọi qua API)
# ============================================

def backend_retriever(question: str, top_k: int = 5, use_hybrid: bool = False, use_rerank: bool = False) -> List[Dict[str, Any]]:
    """
    Gọi backend API để retrieve documents.
    
    Args:
        question: Search query
        top_k: Number of results
        use_hybrid: Use hybrid search (BM25 + Vector) instead of pure semantic
        use_rerank: Use LLM re-ranking to reorder results
    """
    try:
        logger.info(f"GỌI BACKEND API: {SEARCH_ENDPOINT}")
        logger.info(f"Query: {question[:60]}... (top_k={top_k}, hybrid={use_hybrid}, rerank={use_rerank})")
        
        # Select search mode
        search_mode = "hybrid" if use_hybrid else "semantic"
        
        # Gọi backend search endpoint (POST with Query parameters)
        response = httpx.post(
            SEARCH_ENDPOINT,
            params={
                "keyword": question,
                "mode": search_mode,  # hybrid or semantic
                "limit": top_k,
                "rerank": use_rerank  # Enable LLM re-ranking
            },
            timeout=60.0  # Longer timeout for re-ranking
        )
        
        if response.status_code != 200:
            logger.error(f"Backend returned {response.status_code}: {response.text}")
            return []
        
        data = response.json()
        results = data.get("results", [])
        
        logger.info(f"✓ Retrieved {len(results)} documents từ backend [{search_mode}]")
        
        # Convert kết quả thành format giống langchain Document
        documents = []
        for result in results:
            doc = {
                "page_content": result.get("content", result.get("description", "")),
                "metadata": {
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "type": result.get("type"),
                    "year": result.get("year"),
                    "authority": result.get("authority"),
                }
            }
            documents.append(doc)
        
        return documents
        
    except httpx.ConnectError as e:
        logger.error(f"✗ Không thể kết nối tới backend: {e}")
        logger.error(f"Đảm bảo backend đang chạy tại {BACKEND_URL}")
        return []
    except Exception as e:
        logger.error(f"Lỗi khi gọi backend retriever: {e}")
        return []


def create_retriever_func(top_k: int = 5, use_hybrid: bool = False, use_rerank: bool = False):
    """
    Wrapper function cho retriever
    
    Args:
        top_k: Number of results to retrieve
        use_hybrid: Use hybrid search (BM25 + vector)
        use_rerank: Use LLM re-ranking
    """
    def _retriever(question: str):
        return backend_retriever(
            question,
            top_k=top_k,
            use_hybrid=use_hybrid,
            use_rerank=use_rerank
        )
    return _retriever


# ============================================
# ANSWER GENERATOR (dùng kết quả từ backend)
# ============================================

def answer_generator(question: str, llm, top_k: int = 5, use_hybrid: bool = False, use_rerank: bool = False) -> str:
    """
    Generate answer từ backend retrieval + LLM
    """
    try:
        logger.debug(f"Generating answer for: {question[:50]}...")
        
        # Bước 1: Retrieve từ backend
        retrieved_docs = backend_retriever(question, top_k=top_k, use_hybrid=use_hybrid, use_rerank=use_rerank)
        
        if not retrieved_docs:
            logger.warning("Không lấy được document từ backend")
            context = "Không tìm thấy thông tin phù hợp"
        else:
            # Lấy top 3 docs
            context = "\n\n".join([
                doc.get("page_content", doc.get("description", ""))[:1000]
                for doc in retrieved_docs[:3]
            ])
        
        # Bước 2: Tạo prompt
        prompt = f"""Dựa trên thông tin pháp luật sau, hãy trả lời câu hỏi một cách chính xác, rõ ràng và chi tiết:

Thông tin:
{context}

Câu hỏi: {question}

Hãy trả lời ngắn gọn, chính xác, dựa trên thông tin được cung cấp."""
        
        # Bước 3: Gọi LLM
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"Generated answer: {answer[:60]}...")
        return answer
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return f"Lỗi: Không thể tạo câu trả lời"


def create_answer_generator_func(llm, top_k: int = 5, use_hybrid: bool = False, use_rerank: bool = False):
    """Wrapper function cho answer generator"""
    def _answer_gen(question: str):
        return answer_generator(question, llm, top_k=top_k, use_hybrid=use_hybrid, use_rerank=use_rerank)
    return _answer_gen


# ============================================
# MAIN EVALUATION FUNCTION
# ============================================

def run_evaluation(config_tier: str, sample_size: int = None, verbose: bool = False):
    """
    Chạy evaluation pipeline
    
    Args:
        config_tier: 'dev', 'staging', hoặc 'prod'
        sample_size: Số test cases để chạy (None = tất cả)
        verbose: Chi tiết log
    """
    
    # 1. Select config
    config_map = {
        'dev': DEV_CONFIG,
        'staging': STAGING_CONFIG,
        'prod': PROD_CONFIG
    }
    config = config_map.get(config_tier, PROD_CONFIG)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Starting Evaluation - {config_tier.upper()} Configuration")
    logger.info(f"Backend: {BACKEND_URL}")
    logger.info(f"{'='*80}\n")
    
    # 2. Check backend connection
    logger.info("Checking backend connection...")
    try:
        response = httpx.get(f"{BACKEND_URL}/docs", timeout=5.0)
        if response.status_code == 200:
            logger.info("✓ Backend is running")
        else:
            logger.warning(f"Backend returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Cannot connect to backend at {BACKEND_URL}")
        logger.error(f"Error: {e}")
        logger.error("Please start backend: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # 3. Initialize LLM
    logger.info("Initializing OpenAI LLM...")
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.0
        )
        logger.info("✓ LLM initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        return False
    
    # 4. Load test dataset
    logger.info("Loading test dataset...")
    test_file = "tests/evaluation_dataset.json"
    
    if not os.path.exists(test_file):
        logger.error(f"Test file not found: {test_file}")
        return False
    
    try:
        dataset = TestDatasetManager.load_dataset(test_file)
        errors = TestDatasetManager.validate_dataset(dataset)
        
        if errors:
            logger.error("Dataset validation errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        test_cases = dataset['test_cases']
        
        # Apply sampling if requested
        if sample_size:
            test_cases = test_cases[:sample_size]
        
        logger.info(f"✓ Loaded {len(test_cases)} test cases")
        
    except Exception as e:
        logger.error(f"Error loading test dataset: {e}")
        return False
    
    # 5. Initialize evaluators
    logger.info("Initializing evaluators...")
    batch_evaluator = BatchEvaluator(config)
    batch_evaluator.set_llm(llm)
    
    # 6. Create retriever and answer generator (gọi qua backend)
    logger.info("Setting up backend retriever and answer generator...")
    logger.info("Using SEMANTIC search (V1 baseline - best results)")
    retriever = create_retriever_func(
        top_k=config.retriever.top_k,
        use_hybrid=False,  # Revert to semantic only
        use_rerank=False   # Disable re-ranking
    )
    answer_gen = create_answer_generator_func(
        llm, 
        top_k=config.retriever.top_k,
        use_hybrid=False,  # Semantic only
        use_rerank=False   # No re-ranking
    )
    
    # 7. Run batch evaluation
    logger.info(f"\n{'='*80}")
    logger.info("Running Batch Evaluation via Backend...")
    logger.info(f"{'='*80}\n")
    
    try:
        batch_result = batch_evaluator.run_evaluation(
            test_cases=test_cases,
            retriever=retriever,
            answer_generator=answer_gen,
            batch_id=f"eval_{config_tier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return False
    
    # 8. Generate reports
    logger.info("\nGenerating reports...")
    report_gen = ReportGenerator(config)
    
    try:
        report = report_gen.generate_report(
            batch_result,
            model_name="LegalChatbot-RAG-v1",
            knowledge_base_version="2024-03-21"
        )
        
        # Save in multiple formats
        report_gen.save_report_json(report)
        report_gen.save_report_csv(batch_result)
        report_gen.save_report_html(report)
        
        logger.info(f"✓ Reports saved to: {config.reporting.output_dir}")
        
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        return False
    
    # 9. Print summary
    print_summary(batch_result, report)
    
    # 10. Return deployment readiness
    return report.ready_for_deployment


def print_summary(batch_result, report):
    """In bản tóm tắt kết quả - focus on quality metrics"""
    
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"SYSTEM QUALITY: {report.overall_quality}")
    print(f"  Status: {'✓ Ready' if report.ready_for_deployment else '⚠ Needs Review'}\n")
    
    print(f"ANSWER GENERATION QUALITY (Primary)")
    print(f"  Accuracy: {batch_result.avg_accuracy:.2f}/5 {'[EXCELLENT]' if batch_result.avg_accuracy >= 4.6 else '[GOOD]' if batch_result.avg_accuracy >= 4.3 else '[OK]'}")
    print(f"  Completeness: {batch_result.avg_completeness:.2f}/5 {'[GOOD]' if batch_result.avg_completeness >= 4.0 else '[OK]'}")
    print(f"  Relevance: {batch_result.avg_relevance:.2f}/5 {'[EXCELLENT]' if batch_result.avg_relevance >= 4.6 else '[GOOD]' if batch_result.avg_relevance >= 4.2 else '[OK]'}")
    print(f"  Overall Score: {batch_result.avg_overall_score:.2f}/5\n")
    
    print(f"RETRIEVAL METRICS (Supporting)")
    print(f"  MRR: {batch_result.avg_mrr:.3f} {'[GOOD]' if batch_result.avg_mrr >= 0.62 else '[OK]'}")
    print(f"  nDCG: {batch_result.avg_ndcg:.3f} {'[GOOD]' if batch_result.avg_ndcg >= 0.62 else '[OK]'}")
    print(f"  Coverage: {batch_result.avg_keyword_coverage:.1f}%\n")
    
    print(f"QUALITY GATES: {'✓ PASSED' if batch_result.quality_gates_passed else '✗ NOT PASSED'}\n")


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='RAG Evaluation for Legal Chatbot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python RUN_EVALUATION.py --config dev --sample 5
  python RUN_EVALUATION.py --config staging
  python RUN_EVALUATION.py --config prod
        """
    )
    
    parser.add_argument(
        '--config',
        choices=['dev', 'staging', 'prod'],
        default='dev',
        help='Configuration tier (default: dev)'
    )
    parser.add_argument(
        '--sample',
        type=int,
        help='Number of test cases to run (default: all)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    # Run evaluation
    success = run_evaluation(
        config_tier=args.config,
        sample_size=args.sample,
        verbose=args.verbose
    )
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
