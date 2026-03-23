"""
Production-Grade RAG Evaluation - Example Usage

This script demonstrates how to use the evaluation framework.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tests.evaluation.config import EvaluationConfig, PROD_CONFIG
from tests.evaluation.batch_eval import BatchEvaluator
from tests.evaluation.reporting import ReportGenerator
from app.core.config import settings
from langchain_openai import ChatOpenAI


# Configure logging with UTF-8 support for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Fix console encoding on Windows for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_test_cases(test_file: str) -> list:
    """Load test cases from JSON file"""
    logger.info(f"Loading test cases from {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_cases = data.get('test_cases', [])
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    return test_cases


def example_retriever(question: str):
    """
    Example retriever function. Replace with your actual retriever.
    
    Should return List[Any] where each item has 'page_content' or 'content'
    """
    # In real scenario, this would call:
    # retriever = vector_store.as_retriever()
    # chunks = retriever.invoke(question)
    
    # Mock retrieval for demonstration
    mock_chunks = [
        {
            'page_content': f'Information about {question}',
            'metadata': {'source': 'doc1'},
            'score': 0.95
        },
        {
            'page_content': f'Related info to {question}',
            'metadata': {'source': 'doc2'},
            'score': 0.85
        }
    ]
    return mock_chunks


def example_answer_generator(question: str):
    """
    Example answer generator. Replace with your actual LLM.
    
    Should return str (the answer)
    """
    # In real scenario:
    # chain = retrieve_and_generate_chain()
    # answer = chain.invoke({"question": question})
    
    return f"This is an answer to: {question}"


def run_evaluation():
    """Run the evaluation pipeline"""
    
    logger.info("="*80)
    logger.info("Starting Production-Grade RAG Evaluation")
    logger.info("="*80)
    
    # Step 1: Initialize configuration
    logger.info("\nStep 1: Initializing configuration...")
    # Use production config for strict evaluation
    config = PROD_CONFIG
    logger.info(f"Configuration: {config}")
    
    # Step 2: Load test cases
    logger.info("\nStep 2: Loading test cases...")
    test_file = "tests/evaluation_dataset.json"
    
    if not os.path.exists(test_file):
        logger.warning(f"Test file not found: {test_file}")
        logger.info("Creating sample test dataset...")
        create_sample_test_dataset(test_file)
    
    test_cases = load_test_cases(test_file)
    
    # Step 3: Initialize evaluators
    logger.info("\nStep 3: Initializing evaluators...")
    batch_evaluator = BatchEvaluator(config)
    report_generator = ReportGenerator(config)
    
    # Set up LLM for answer evaluation
    try:
        logger.info("Setting up OpenAI LLM...")
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.0
        )
        batch_evaluator.set_llm(llm)
        logger.info("LLM initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to set LLM: {e}. Answer evaluation will use default scores.")
    
    # Step 4: Run batch evaluation
    logger.info("\nStep 4: Running batch evaluation...")
    logger.info(f"Evaluating {len(test_cases)} test cases...")
    
    try:
        batch_result = batch_evaluator.run_evaluation(
            test_cases=test_cases,
            retriever=example_retriever,
            answer_generator=example_answer_generator,
            batch_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        return False
    
    # Step 5: Generate report
    logger.info("\nStep 5: Generating report...")
    report = report_generator.generate_report(
        batch_result,
        model_name="LegalChatbot-v1",
        knowledge_base_version="1.0"
    )
    
    # Step 6: Save reports in multiple formats
    logger.info("\nStep 6: Saving reports...")
    
    # JSON report
    json_report_path = report_generator.save_report_json(report)
    logger.info(f"JSON report: {json_report_path}")
    
    # CSV report
    csv_report_path = report_generator.save_report_csv(batch_result)
    logger.info(f"CSV report: {csv_report_path}")
    
    # HTML report
    html_report_path = report_generator.save_report_html(report)
    logger.info(f"HTML report: {html_report_path}")
    
    # Step 7: Print summary
    logger.info("\n" + "="*80)
    logger.info("EVALUATION SUMMARY")
    logger.info("="*80)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║            RAG EVALUATION RESULTS - PRODUCTION GRADE                      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Batch ID:           {batch_result.batch_id:<52} ║
║ Total Tests:        {batch_result.total_tests:<52} ║
║ Passed:             {batch_result.passed_tests:<52} ║
║ Failed:             {batch_result.failed_tests:<52} ║
║ Errors:             {batch_result.error_tests:<52} ║
║ Success Rate:       {batch_result.success_rate:.1f}%{' '*46} ║
║ Error Rate:         {batch_result.error_rate:.1f}%{' '*46} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ RETRIEVAL METRICS                                                         ║
╠─────────────────────────────────────────────────────────────────────────────║
║ Avg MRR:            {batch_result.avg_mrr:.3f}{' '*43} ║
║ Avg nDCG:           {batch_result.avg_ndcg:.3f}{' '*43} ║
║ Avg Coverage:       {batch_result.avg_keyword_coverage:.1f}%{' '*43} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ ANSWER QUALITY METRICS                                                    ║
╠─────────────────────────────────────────────────────────────────────────────║
║ Avg Accuracy:       {batch_result.avg_accuracy:.2f}/5{' '*41} ║
║ Avg Completeness:   {batch_result.avg_completeness:.2f}/5{' '*41} ║
║ Avg Relevance:      {batch_result.avg_relevance:.2f}/5{' '*41} ║
║ Avg Overall Score:  {batch_result.avg_overall_score:.2f}/5{' '*41} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ QUALITY ASSESSMENT                                                        ║
╠─────────────────────────────────────────────────────────────────────────────║
║ Overall Quality:    {report.overall_quality:<52} ║
║ Quality Gates:      {'PASSED' if batch_result.quality_gates_passed else 'FAILED':<52} ║
║ Ready for Deploy:   {'YES' if report.ready_for_deployment else 'NO':<52} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ RECOMMENDATIONS                                                           ║
╠─────────────────────────────────────────────────────────────────────────────║
    """)
    
    for i, rec in enumerate(report.recommendations, 1):
        print(f"║ {i}. {rec:<73} ║")
    
    print(f"""╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 8: Final decision
    logger.info("="*80)
    if report.ready_for_deployment:
        logger.info("✓ DEPLOYMENT APPROVED - System is ready for production")
    else:
        logger.warning("✗ DEPLOYMENT BLOCKED - Issues need to be resolved before deployment")
    
    logger.info(f"Reports saved to: {config.reporting.output_dir}")
    logger.info("="*80)
    
    return report.ready_for_deployment


def create_sample_test_dataset(output_file: str):
    """Create a sample test dataset for demonstration"""
    
    sample_data = {
        "test_cases": [
            {
                "id": "test_001",
                "category": "admission",
                "question": "Thủ tục cần thiết để học đại học tại Hàn Quốc là gì?",
                "expected_keywords": ["visa", "topik", "gpa", "chứng chỉ"],
                "reference_answer": "Để học đại học tại Hàn Quốc, bạn cần: 1) Chuẩn bị hồ sơ học bạ, 2) Có chứng chỉ Tiếng Anh (TOEFL, IELTS), 3) Ghi danh thi TOPIK nếu chương trình tiếng Hàn, 4) Nộp đơn từ 4-6 tháng trước, 5) Phỏng vấn online, 6) Xin visa học tập D-2.",
                "difficulty": "medium",
                "priority": "high"
            },
            {
                "id": "test_002",
                "category": "visa",
                "question": "Loại visa nào để du học Hàn Quốc?",
                "expected_keywords": ["D-2 visa", "thời hạn", "yêu cầu"],
                "reference_answer": "Sinh viên quốc tế sử dụng D-2 visa. Loại visa này có thời hạn từ 1-2 năm và có thể gia hạn hàng năm. Yêu cầu bao gồm: Thư mời từ trường, bằng cấp, chứng minh tài chính.",
                "difficulty": "easy",
                "priority": "high"
            },
            {
                "id": "test_003",
                "category": "tuition",
                "question": "Học phí trung bình tại các đại học Hàn Quốc là bao nhiêu?",
                "expected_keywords": ["học phí", "triệu won", "bậc cử nhân"],
                "reference_answer": "Học phí cho bậc cử nhân: 6-10 triệu won/năm. Các trường top (Seoul National University): 8-10 triệu won/năm. Các trường khác: 4-7 triệu won/năm. Bậc thạc sĩ: 7-15 triệu won/năm.",
                "difficulty": "medium",
                "priority": "medium"
            },
            {
                "id": "test_004",
                "category": "living",
                "question": "Chi phí sinh sống hàng tháng ở Seoul là bao nhiêu?",
                "expected_keywords": ["tiền nhà", "ăn uống", "giao thông"],
                "reference_answer": "Chi phí sinh sống tại Seoul vào khoảng 1.5-2 triệu won/tháng. Chi tiết: Nhà trọ (500K-1M won), Ăn uống (300-500K won), Giao thông (100K won), Khác (200K won).",
                "difficulty": "easy",
                "priority": "medium"
            },
            {
                "id": "test_005",
                "category": "campus_life",
                "question": "Các hoạt động ngoại khóa tại đại học Hàn Quốc?",
                "expected_keywords": ["câu lạc bộ", "sự kiện", "thể thao"],
                "reference_answer": "Đại học Hàn Quốc có nhiều câu lạc bộ: thể thao, văn hóa, học tập. Các sự kiện: Festival đại học, thi thể thao, liên hoan văn nghệ. Sinh viên quốc tế được khuyến khích tham gia.",
                "difficulty": "easy",
                "priority": "low"
            }
        ],
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "total_tests": 5,
            "categories": ["admission", "visa", "tuition", "living", "campus_life"]
        }
    }
    
    # Create directory if not exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Sample test dataset created: {output_file}")


if __name__ == "__main__":
    try:
        success = run_evaluation()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
