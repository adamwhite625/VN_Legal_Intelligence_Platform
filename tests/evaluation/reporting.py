"""
Evaluation Reporting - Production Grade

Generates comprehensive reports in multiple formats.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from .config import EvaluationConfig, ReportingConfig
from .metrics import EvaluationBatchResult, EvaluationReport


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates evaluation reports"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.reporting_config = config.reporting
        self._ensure_output_dirs()
    
    def _ensure_output_dirs(self) -> None:
        """Ensure output directories exist"""
        Path(self.reporting_config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.reporting_config.artifact_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        batch_result: EvaluationBatchResult,
        model_name: str = "Unknown",
        knowledge_base_version: str = "1.0"
    ) -> EvaluationReport:
        """
        Generate comprehensive evaluation report.
        
        Args:
            batch_result: Batch evaluation results
            model_name: Name of evaluated model
            knowledge_base_version: KB version
            
        Returns:
            EvaluationReport
        """
        logger.info("Generating evaluation report...")
        
        # Analyze results
        strengths = self._identify_strengths(batch_result)
        weaknesses = self._identify_weaknesses(batch_result)
        recommendations = self._generate_recommendations(batch_result)
        
        # Determine overall quality
        overall_quality = self._assess_overall_quality(batch_result)
        ready_for_deployment = (
            overall_quality in ["EXCELLENT", "GOOD"] and
            batch_result.quality_gates_passed
        )
        
        report = EvaluationReport(
            report_id=f"report_{batch_result.batch_id}",
            evaluated_model=model_name,
            knowledge_base_version=knowledge_base_version,
            batch_results=batch_result,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            overall_quality=overall_quality,
            ready_for_deployment=ready_for_deployment
        )
        
        return report
    
    def save_report_json(
        self,
        report: EvaluationReport,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save report as JSON.
        
        Args:
            report: EvaluationReport
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report.batch_results.batch_id}.json"
        
        output_path = Path(self.reporting_config.output_dir) / filename
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
            
            logger.info(f"Report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving JSON report: {str(e)}")
            raise
    
    def save_report_csv(
        self,
        batch_result: EvaluationBatchResult,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save detailed results as CSV.
        
        Args:
            batch_result: Batch evaluation results
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        import csv
        
        if filename is None:
            filename = f"results_{batch_result.batch_id}.csv"
        
        output_path = Path(self.reporting_config.output_dir) / filename
        
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    "Test ID", "Category", "Difficulty", "Status",
                    "MRR", "nDCG", "Coverage", "Accuracy", "Completeness", 
                    "Relevance", "Overall Score", "Time (s)"
                ])
                
                # Data rows
                for result in batch_result.test_results:
                    writer.writerow([
                        result.test_id,
                        result.category,
                        result.difficulty,
                        result.status,
                        f"{result.retrieval_metrics.mrr:.3f}",
                        f"{result.retrieval_metrics.ndcg:.3f}",
                        f"{result.retrieval_metrics.keyword_coverage:.1f}",
                        f"{result.answer_metrics.accuracy:.2f}",
                        f"{result.answer_metrics.completeness:.2f}",
                        f"{result.answer_metrics.relevance:.2f}",
                        f"{result.answer_metrics.overall_score:.2f}",
                        f"{result.execution_time:.2f}"
                    ])
            
            logger.info(f"CSV report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving CSV report: {str(e)}")
            raise
    
    def save_report_html(
        self,
        report: EvaluationReport,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save report as HTML.
        
        Args:
            report: EvaluationReport
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"report_{report.batch_results.batch_id}.html"
        
        output_path = Path(self.reporting_config.output_dir) / filename
        
        try:
            html_content = self._generate_html_report(report)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving HTML report: {str(e)}")
            raise
    
    def _generate_html_report(self, report: EvaluationReport) -> str:
        """Generate HTML report content"""
        batch = report.batch_results
        
        # Status indicators
        overall_quality_color = {
            "EXCELLENT": "#28a745",
            "GOOD": "#17a2b8",
            "ACCEPTABLE": "#ffc107",
            "NEEDS_IMPROVEMENT": "#dc3545"
        }.get(report.overall_quality, "#666")
        
        # Determine if quality gates passed
        gates_passed = (
            batch.avg_mrr >= 0.62 and
            batch.avg_ndcg >= 0.62 and
            batch.avg_accuracy >= 4.4
        )
        gates_color = "#28a745" if gates_passed else "#dc3545"
        gates_status = "PASSED" if gates_passed else "FAILED"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Evaluation Report - {report.report_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Courier, monospace; background: #1e1e1e; color: #e0e0e0; }}
        .container {{ max-width: 900px; margin: 20px auto; background: #2d2d2d; 
                       padding: 30px; border-radius: 4px; border: 1px solid #444; }}
        header {{ border-bottom: 2px solid #0066cc; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: #0066cc; font-size: 1.8em; margin-bottom: 10px; }}
        .report-meta {{ font-size: 0.9em; color: #888; }}
        .report-meta p {{ margin: 3px 0; }}
        
        .section {{ margin: 25px 0; }}
        .section-title {{ color: #0066cc; font-size: 1.1em; font-weight: bold; margin: 15px 0 12px 0; }}
        .metric-row {{ display: flex; justify-content: space-between; margin: 8px 0; font-size: 0.95em; }}
        .metric-name {{ min-width: 300px; }}
        .metric-value {{ font-weight: bold; }}
        
        .quality-badge {{ display: inline-block; padding: 4px 12px; border-radius: 3px; 
                          font-weight: bold; font-size: 0.9em; margin-top: 5px; margin-right: 10px; }}
        .status-pass {{ color: #28a745; }}
        .status-fail {{ color: #dc3545; }}
        .status-info {{ color: #0066cc; }}
        
        .gates-section {{ padding: 15px; border-left: 3px solid {gates_color}; margin: 15px 0; background: #333; border-radius: 3px; }}
        .gates-status {{ color: {gates_color}; font-weight: bold; font-size: 1.05em; }}
        
        footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #444; color: #888; font-size: 0.85em; }}
        
        code {{ background: #1e1e1e; padding: 1px 3px; border-radius: 2px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>[EVALUATION REPORT]</h1>
            <div class="report-meta">
                <p>Report ID: {report.report_id}</p>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>Model: {report.evaluated_model}</p>
            </div>
        </header>
        
        <div class="section">
            <div class="section-title">SYSTEM QUALITY</div>
            <div class="metric-row">
                <span class="metric-name">Overall Status:</span>
                <span class="metric-value" style="color: {overall_quality_color};">{report.overall_quality}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Ready for Deployment:</span>
                <span class="metric-value" style="color: {'#28a745' if report.ready_for_deployment else '#dc3545'};">
                    {'YES' if report.ready_for_deployment else 'NO'}
                </span>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">ANSWER GENERATION QUALITY (Primary)</div>
            <div class="metric-row">
                <span class="metric-name">* Accuracy:</span>
                <span class="metric-value">{batch.avg_accuracy:.2f}/5 {self._get_quality_label(batch.avg_accuracy)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">* Completeness:</span>
                <span class="metric-value">{batch.avg_completeness:.2f}/5 {self._get_quality_label(batch.avg_completeness)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">* Relevance:</span>
                <span class="metric-value">{batch.avg_relevance:.2f}/5 {self._get_quality_label(batch.avg_relevance)}</span>
            </div>
            <div class="metric-row" style="font-weight: bold; margin-top: 10px;">
                <span class="metric-name">Overall Score:</span>
                <span class="metric-value">{batch.avg_overall_score:.2f}/5</span>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">RETRIEVAL METRICS (Supporting)</div>
            <div class="metric-row">
                <span class="metric-name">* Mean Reciprocal Rank (MRR):</span>
                <span class="metric-value">{batch.avg_mrr:.3f} {self._get_retrieval_label(batch.avg_mrr)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">* Normalized DCG (nDCG):</span>
                <span class="metric-value">{batch.avg_ndcg:.3f} {self._get_retrieval_label(batch.avg_ndcg)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">* Keyword Coverage:</span>
                <span class="metric-value">{batch.avg_keyword_coverage:.1f}%</span>
            </div>
        </div>
        
        <div class="gates-section">
            <div class="section-title" style="margin-top: 0; color: {gates_color};">QUALITY GATES</div>
            <div class="gates-status">{gates_status}</div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                <div>MRR >= 0.62: {'✓' if batch.avg_mrr >= 0.62 else '✗'} ({batch.avg_mrr:.3f})</div>
                <div>nDCG >= 0.62: {'✓' if batch.avg_ndcg >= 0.62 else '✗'} ({batch.avg_ndcg:.3f})</div>
                <div>Accuracy >= 4.4: {'✓' if batch.avg_accuracy >= 4.4 else '✗'} ({batch.avg_accuracy:.2f})</div>
            </div>
        </div>
        
        <footer>
            <p>Generated by: Legal Chatbot RAG Evaluation Framework v1.0</p>
            <p>Tests executed: {batch.total_tests}</p>
        </footer>
    </div>
</body>
</html>"""
        return html
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label badge for answer metrics"""
        if score >= 4.6:
            return '[EXCELLENT]'
        elif score >= 4.3:
            return '[GOOD]'
        elif score >= 3.8:
            return '[ACCEPTABLE]'
        else:
            return '[NEEDS_IMPROVEMENT]'
    
    def _get_retrieval_label(self, score: float) -> str:
        """Get quality label badge for retrieval metrics"""
        if score >= 0.8:
            return '[EXCELLENT]'
        elif score >= 0.7:
            return '[GOOD]'
        elif score >= 0.6:
            return '[ACCEPTABLE]'
        else:
            return '[NEEDS_IMPROVEMENT]'
    
    def _identify_strengths(self, batch_result: EvaluationBatchResult) -> List[str]:
        """Identify system strengths"""
        strengths = []
        
        if batch_result.avg_mrr >= 0.8:
            strengths.append("Excellent retrieval performance (MRR >= 0.8)")
        
        if batch_result.avg_accuracy >= 4.7:
            strengths.append("Outstanding answer accuracy (>= 4.7/5)")
        
        if batch_result.success_rate >= 90:
            strengths.append(f"High success rate ({batch_result.success_rate}%)")
        
        if batch_result.error_rate < 2:
            strengths.append("Reliable system with minimal errors")
        
        return strengths or ["System meets acceptable standards"]
    
    def _identify_weaknesses(self, batch_result: EvaluationBatchResult) -> List[str]:
        """Identify system weaknesses"""
        weaknesses = []
        
        if batch_result.avg_mrr < 0.7:
            weaknesses.append(f"Low retrieval ranking (MRR {batch_result.avg_mrr:.3f} < 0.7)")
        
        if batch_result.avg_accuracy < 4.0:
            weaknesses.append(f"Low answer accuracy ({batch_result.avg_accuracy:.2f}/5 < 4.0)")
        
        if batch_result.success_rate < 70:
            weaknesses.append(f"Low success rate ({batch_result.success_rate}% < 70%)")
        
        if batch_result.error_rate > 5:
            weaknesses.append(f"High error rate ({batch_result.error_rate}% > 5%)")
        
        # Check by category
        poor_categories = [
            cat for cat, data in batch_result.category_results.items()
            if data.get("accuracy", 5) < 4.0
        ]
        if poor_categories:
            weaknesses.append(f"Poor performance in: {', '.join(poor_categories)}")
        
        return weaknesses or ["No significant weaknesses identified"]
    
    def _generate_recommendations(self, batch_result: EvaluationBatchResult) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        if batch_result.avg_mrr < 0.7:
            recommendations.append(
                "Improve embedding model or adjust chunking strategy for better retrieval"
            )
        
        if batch_result.avg_accuracy < 4.0:
            recommendations.append("Refine prompt engineering or answer generation logic")
        
        poor_categories = [
            (cat, data) for cat, data in batch_result.category_results.items()
            if data.get("accuracy", 5) < 4.0
        ]
        if poor_categories:
            for cat, _ in poor_categories:
                recommendations.append(f"Focus improvement efforts on '{cat}' category")
        
        if batch_result.error_rate > 2:
            recommendations.append("Add error handling and logging for debugging")
        
        if batch_result.avg_completeness < 4.2:
            recommendations.append("Enhance answer generation to be more comprehensive")
        
        return recommendations or ["System is ready for production"]
    
    def _assess_overall_quality(self, batch_result: EvaluationBatchResult) -> str:
        """Assess overall quality level"""
        avg_score = batch_result.avg_overall_score
        avg_accuracy = batch_result.avg_accuracy
        
        # Quality assessment based on answer quality (more reliable than pass rate)
        if avg_score >= 4.6 and avg_accuracy >= 4.6:
            return "EXCELLENT"
        elif avg_score >= 4.3 and avg_accuracy >= 4.3:
            return "GOOD"
        elif avg_score >= 3.8 and avg_accuracy >= 3.8:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"
