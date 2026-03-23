"""
Evaluation Utilities - Helper Functions

Utility functions for common evaluation tasks.
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TestDatasetManager:
    """Manage test dataset operations"""
    
    @staticmethod
    def load_dataset(filepath: str) -> Dict[str, Any]:
        """Load test dataset from JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_dataset(data: Dict[str, Any], filepath: str) -> None:
        """Save test dataset to JSON"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def validate_dataset(data: Dict[str, Any]) -> List[str]:
        """Validate dataset structure and content"""
        errors = []
        
        if 'test_cases' not in data:
            errors.append("Missing 'test_cases' key")
            return errors
        
        test_cases = data.get('test_cases', [])
        
        if not test_cases:
            errors.append("No test cases found")
            return errors
        
        required_fields = ['id', 'question', 'expected_keywords', 'reference_answer']
        
        for i, case in enumerate(test_cases):
            for field in required_fields:
                if field not in case:
                    errors.append(f"Test case {i}: missing '{field}'")
        
        return errors
    
    @staticmethod
    def split_dataset(
        data: Dict[str, Any],
        train_ratio: float = 0.7,
        seed: int = 42
    ) -> tuple:
        """Split dataset into train/test"""
        import random
        random.seed(seed)
        
        test_cases = data['test_cases']
        random.shuffle(test_cases)
        
        split_idx = int(len(test_cases) * train_ratio)
        
        train_data = data.copy()
        train_data['test_cases'] = test_cases[:split_idx]
        
        test_data = data.copy()
        test_data['test_cases'] = test_cases[split_idx:]
        
        return train_data, test_data
    
    @staticmethod
    def filter_by_category(
        data: Dict[str, Any],
        categories: List[str]
    ) -> Dict[str, Any]:
        """Filter test cases by category"""
        filtered_data = data.copy()
        filtered_data['test_cases'] = [
            case for case in data['test_cases']
            if case.get('category') in categories
        ]
        return filtered_data
    
    @staticmethod
    def filter_by_difficulty(
        data: Dict[str, Any],
        difficulties: List[str]
    ) -> Dict[str, Any]:
        """Filter test cases by difficulty"""
        filtered_data = data.copy()
        filtered_data['test_cases'] = [
            case for case in data['test_cases']
            if case.get('difficulty') in difficulties
        ]
        return filtered_data


class ResultsAnalyzer:
    """Analyze evaluation results"""
    
    @staticmethod
    def compare_results(
        current: Dict[str, Any],
        baseline: Dict[str, Any],
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """Compare current vs baseline results"""
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'regression_detected': False,
            'improvement_detected': False
        }
        
        for metric in ['avg_mrr', 'avg_ndcg', 'avg_accuracy', 'avg_completeness']:
            curr_val = current.get(metric, 0)
            base_val = baseline.get(metric, 0)
            
            if base_val > 0:
                change = (curr_val - base_val) / base_val
            else:
                change = 0
            
            comparison['metrics'][metric] = {
                'current': curr_val,
                'baseline': base_val,
                'change': round(change, 4),
                'change_percent': round(change * 100, 2)
            }
            
            # Check for regression/improvement
            if change < -threshold:
                comparison['regression_detected'] = True
            elif change > threshold:
                comparison['improvement_detected'] = True
        
        return comparison
    
    @staticmethod
    def identify_error_patterns(
        test_results: List[Any]
    ) -> Dict[str, Any]:
        """Identify patterns in failed tests"""
        
        patterns = {
            'by_category': {},
            'by_difficulty': {},
            'common_keywords': {},
            'error_types': {}
        }
        
        for result in test_results:
            if result.get('status') != 'PASS':
                # By category
                cat = result.get('category', 'unknown')
                patterns['by_category'][cat] = patterns['by_category'].get(cat, 0) + 1
                
                # By difficulty
                diff = result.get('difficulty', 'unknown')
                patterns['by_difficulty'][diff] = patterns['by_difficulty'].get(diff, 0) + 1
                
                # Error type
                error = result.get('error_message', 'unknown')
                patterns['error_types'][error] = patterns['error_types'].get(error, 0) + 1
        
        return patterns
    
    @staticmethod
    def export_csv(
        test_results: List[Any],
        filepath: str
    ) -> None:
        """Export results to CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if not test_results:
                return
            
            # Get all keys from first result
            keys = test_results[0].keys()
            writer = csv.DictWriter(f, fieldnames=keys)
            
            writer.writeheader()
            writer.writerows(test_results)
        
        logger.info(f"Results exported to {filepath}")
    
    @staticmethod
    def generate_summary_report(
        batch_results: Dict[str, Any]
    ) -> str:
        """Generate text summary report"""
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    EVALUATION RESULTS SUMMARY                            ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Batch ID:           {batch_results.get('batch_id', 'N/A'):<52} ║
║ Tests Run:          {batch_results.get('total_tests', 0):<52} ║
║ Passed:             {batch_results.get('passed_tests', 0):<52} ║
║ Success Rate:       {batch_results.get('success_rate', 0)}%{' '*46} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Retrieval Performance                                                     ║
║ ├─ Mean Reciprocal Rank:    {batch_results.get('avg_mrr', 0):.3f}         ║
║ ├─ nDCG:                    {batch_results.get('avg_ndcg', 0):.3f}         ║
║ └─ Keyword Coverage:        {batch_results.get('avg_keyword_coverage', 0):.1f}%          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Answer Quality                                                            ║
║ ├─ Accuracy:                {batch_results.get('avg_accuracy', 0):.2f}/5             ║
║ ├─ Completeness:            {batch_results.get('avg_completeness', 0):.2f}/5             ║
║ ├─ Relevance:               {batch_results.get('avg_relevance', 0):.2f}/5             ║
║ └─ Overall Score:           {batch_results.get('avg_overall_score', 0):.2f}/5             ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Quality Gates:      {'PASSED ✓' if batch_results.get('quality_gates_passed') else 'FAILED ✗':<50} ║
║ Ready for Deploy:   {'YES ✓' if batch_results.get('quality_gates_passed') else 'NO ✗':<50} ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
        return report


class BaselineManager:
    """Manage baseline metrics"""
    
    def __init__(self, baseline_dir: str = "tests/results"):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
    
    def save_baseline(
        self,
        batch_results: Dict[str, Any],
        name: str = "baseline"
    ) -> Path:
        """Save current results as baseline"""
        baseline_file = self.baseline_dir / f"{name}.json"
        
        baseline_data = {
            'timestamp': datetime.now().isoformat(),
            'avg_mrr': batch_results.get('avg_mrr'),
            'avg_ndcg': batch_results.get('avg_ndcg'),
            'avg_accuracy': batch_results.get('avg_accuracy'),
            'avg_completeness': batch_results.get('avg_completeness'),
            'avg_relevance': batch_results.get('avg_relevance'),
            'avg_overall_score': batch_results.get('avg_overall_score'),
            'success_rate': batch_results.get('success_rate'),
            'total_tests': batch_results.get('total_tests')
        }
        
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Baseline saved to {baseline_file}")
        return baseline_file
    
    def load_baseline(self, name: str = "baseline") -> Optional[Dict[str, Any]]:
        """Load baseline metrics"""
        baseline_file = self.baseline_dir / f"{name}.json"
        
        if not baseline_file.exists():
            logger.warning(f"Baseline file not found: {baseline_file}")
            return None
        
        with open(baseline_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_baselines(self) -> List[str]:
        """List all available baselines"""
        return [f.stem for f in self.baseline_dir.glob("*.json")]
    
    def get_baseline_history(self, name: str = "baseline") -> List[Dict]:
        """Get history of baseline changes"""
        history_file = self.baseline_dir / f"{name}_history.jsonl"
        
        history = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    history.append(json.loads(line))
        
        return history
    
    def save_baseline_history(
        self,
        batch_results: Dict[str, Any],
        name: str = "baseline"
    ) -> None:
        """Append to baseline history"""
        history_file = self.baseline_dir / f"{name}_history.jsonl"
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'avg_mrr': batch_results.get('avg_mrr'),
            'avg_accuracy': batch_results.get('avg_accuracy'),
            'success_rate': batch_results.get('success_rate')
        }
        
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


class AlertingSystem:
    """Alert system for evaluation monitoring"""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or {
            'mrr_regression': 0.05,           # 5% drop
            'accuracy_regression': 0.10,       # 0.5 point drop
            'error_rate': 0.05,                # 5% errors
            'failure_rate': 0.30               # 30% failures
        }
        self.alerts = []
    
    def check_metrics(
        self,
        current: Dict[str, Any],
        baseline: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Check metrics against thresholds"""
        self.alerts = []
        
        # Check absolute thresholds
        if current.get('avg_mrr', 1) < 0.7:
            self.alerts.append("⚠️ Low MRR (< 0.7)")
        
        if current.get('avg_accuracy', 5) < 4.0:
            self.alerts.append("⚠️ Low accuracy (< 4.0/5)")
        
        if current.get('error_rate', 0) > self.thresholds['error_rate']:
            self.alerts.append(f"⚠️ High error rate (> {self.thresholds['error_rate']*100}%)")
        
        # Check regression vs baseline
        if baseline:
            mrr_loss = (baseline.get('avg_mrr', 1) - current.get('avg_mrr', 0)) / baseline.get('avg_mrr', 1)
            if mrr_loss > self.thresholds['mrr_regression']:
                self.alerts.append(f"📉 MRR regression ({mrr_loss*100:.1f}%)")
            
            acc_loss = baseline.get('avg_accuracy', 0) - current.get('avg_accuracy', 0)
            if acc_loss > self.thresholds['accuracy_regression']:
                self.alerts.append(f"📉 Accuracy dropped {acc_loss:.2f} points")
        
        return self.alerts
    
    def send_alert(self, alert: str, channel: str = "log") -> None:
        """Send alert through specified channel"""
        if channel == "log":
            logger.warning(alert)
        elif channel == "slack":
            # Implement Slack integration
            pass
        elif channel == "email":
            # Implement email integration
            pass


class PerformanceTracker:
    """Track performance over time"""
    
    def __init__(self, history_file: str = "tests/results/performance_history.jsonl"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_evaluation(self, batch_results: Dict[str, Any]) -> None:
        """Log evaluation result"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'batch_id': batch_results.get('batch_id'),
            'avg_mrr': batch_results.get('avg_mrr'),
            'avg_ndcg': batch_results.get('avg_ndcg'),
            'avg_accuracy': batch_results.get('avg_accuracy'),
            'success_rate': batch_results.get('success_rate'),
            'error_rate': batch_results.get('error_rate')
        }
        
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_trend(self, metric: str, days: int = 30) -> List[Dict]:
        """Get metric trend for last N days"""
        if not self.history_file.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        trend = []
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                timestamp = datetime.fromisoformat(entry['timestamp'])
                
                if timestamp > cutoff_date and metric in entry:
                    trend.append({
                        'timestamp': entry['timestamp'],
                        'value': entry[metric]
                    })
        
        return trend
    
    def generate_trend_report(self, metric: str, days: int = 30) -> str:
        """Generate trend report for a metric"""
        trend = self.get_trend(metric, days)
        
        if not trend:
            return f"No trend data available for {metric}"
        
        values = [t['value'] for t in trend]
        avg_value = sum(values) / len(values) if values else 0
        min_value = min(values)
        max_value = max(values)
        
        # Check trend direction
        if len(values) > 1:
            trend_direction = "📈 Improving" if values[-1] > values[0] else "📉 Declining"
        else:
            trend_direction = "→ Stable"
        
        report = f"""
{metric.upper()} TREND ({days} days)
==================================
Average:  {avg_value:.3f}
Min:      {min_value:.3f}
Max:      {max_value:.3f}
Trend:    {trend_direction}
Samples:  {len(trend)}
"""
        return report
