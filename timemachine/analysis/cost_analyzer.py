"""
Cost Analysis for TimeMachine
Analyzes token usage, costs, and optimization opportunities
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from .llm_tracker import LLMCall


@dataclass
class CostBreakdown:
    """Cost analysis breakdown"""
    total_cost: float
    total_tokens: int
    total_calls: int
    cost_by_model: Dict[str, float]
    tokens_by_model: Dict[str, int]
    calls_by_model: Dict[str, int]
    average_cost_per_call: float
    average_tokens_per_call: float
    most_expensive_calls: List[LLMCall]
    optimization_suggestions: List[str]


@dataclass
class UsagePattern:
    """Usage pattern analysis"""
    model_name: str
    avg_input_tokens: float
    avg_output_tokens: float
    avg_cost_per_call: float
    call_frequency: float
    efficiency_score: float  # 0-100, higher is better


class CostAnalyzer:
    """Analyzes LLM usage costs and provides optimization insights"""
    
    def __init__(self, recorder=None):
        self.recorder = recorder
        
    def analyze_costs(self, graph_run_id: Optional[str] = None, 
                     time_period: Optional[Tuple[datetime, datetime]] = None) -> CostBreakdown:
        """Analyze costs for a specific run or time period"""
        calls = self._get_llm_calls(graph_run_id, time_period)
        
        if not calls:
            return CostBreakdown(
                total_cost=0.0, total_tokens=0, total_calls=0,
                cost_by_model={}, tokens_by_model={}, calls_by_model={},
                average_cost_per_call=0.0, average_tokens_per_call=0.0,
                most_expensive_calls=[], optimization_suggestions=[]
            )
        
        # Calculate totals
        total_cost = sum(call.cost_usd for call in calls)
        total_tokens = sum(call.total_tokens for call in calls)
        total_calls = len(calls)
        
        # Group by model
        cost_by_model = {}
        tokens_by_model = {}
        calls_by_model = {}
        
        for call in calls:
            model = call.model_name
            cost_by_model[model] = cost_by_model.get(model, 0) + call.cost_usd
            tokens_by_model[model] = tokens_by_model.get(model, 0) + call.total_tokens
            calls_by_model[model] = calls_by_model.get(model, 0) + 1
        
        # Calculate averages
        avg_cost = total_cost / total_calls if total_calls > 0 else 0
        avg_tokens = total_tokens / total_calls if total_calls > 0 else 0
        
        # Find most expensive calls
        most_expensive = sorted(calls, key=lambda x: x.cost_usd, reverse=True)[:5]
        
        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(calls, cost_by_model, tokens_by_model)
        
        return CostBreakdown(
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_calls=total_calls,
            cost_by_model=cost_by_model,
            tokens_by_model=tokens_by_model,
            calls_by_model=calls_by_model,
            average_cost_per_call=avg_cost,
            average_tokens_per_call=avg_tokens,
            most_expensive_calls=most_expensive,
            optimization_suggestions=suggestions
        )
    
    def analyze_usage_patterns(self, days: int = 7) -> List[UsagePattern]:
        """Analyze usage patterns over time"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        calls = self._get_llm_calls(time_period=(start_time, end_time))
        
        if not calls:
            return []
        
        # Group by model
        model_calls = {}
        for call in calls:
            model = call.model_name
            if model not in model_calls:
                model_calls[model] = []
            model_calls[model].append(call)
        
        patterns = []
        for model, model_call_list in model_calls.items():
            pattern = self._analyze_model_pattern(model, model_call_list, days)
            patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x.efficiency_score, reverse=True)
    
    def _analyze_model_pattern(self, model_name: str, calls: List[LLMCall], days: int) -> UsagePattern:
        """Analyze usage pattern for a specific model"""
        if not calls:
            return UsagePattern(model_name, 0, 0, 0, 0, 0)
        
        # Calculate averages
        avg_input = statistics.mean(call.input_tokens for call in calls)
        avg_output = statistics.mean(call.output_tokens for call in calls)
        avg_cost = statistics.mean(call.cost_usd for call in calls)
        
        # Calculate frequency (calls per day)
        frequency = len(calls) / days
        
        # Calculate efficiency score (subjective metric)
        efficiency = self._calculate_efficiency_score(model_name, avg_input, avg_output, avg_cost)
        
        return UsagePattern(
            model_name=model_name,
            avg_input_tokens=avg_input,
            avg_output_tokens=avg_output,
            avg_cost_per_call=avg_cost,
            call_frequency=frequency,
            efficiency_score=efficiency
        )
    
    def _calculate_efficiency_score(self, model_name: str, avg_input: float, 
                                   avg_output: float, avg_cost: float) -> float:
        """Calculate efficiency score (0-100, higher is better)"""
        # Base score starts at 50
        score = 50.0
        
        # Adjust for model efficiency (cost per token)
        cost_per_token = avg_cost / (avg_input + avg_output) if (avg_input + avg_output) > 0 else 0
        
        # Lower cost per token = higher efficiency
        if cost_per_token < 0.00001:  # Very cheap
            score += 30
        elif cost_per_token < 0.0001:  # Cheap
            score += 20
        elif cost_per_token < 0.001:  # Moderate
            score += 10
        elif cost_per_token > 0.01:  # Expensive
            score -= 20
        
        # Adjust for output/input ratio (more output per input = better)
        if avg_input > 0:
            output_ratio = avg_output / avg_input
            if output_ratio > 2:  # Good output generation
                score += 15
            elif output_ratio > 1:
                score += 10
            elif output_ratio < 0.5:  # Poor output generation
                score -= 10
        
        # Adjust for model capabilities
        if 'gpt-4' in model_name.lower():
            score += 5  # Higher quality
        elif 'claude-3-opus' in model_name.lower():
            score += 5  # Higher quality
        elif 'gpt-3.5' in model_name.lower():
            score += 10  # Good balance
        
        return max(0, min(100, score))
    
    def _generate_optimization_suggestions(self, calls: List[LLMCall], 
                                         cost_by_model: Dict[str, float],
                                         tokens_by_model: Dict[str, int]) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        if not calls:
            return suggestions
        
        # Check for expensive models
        total_cost = sum(cost_by_model.values())
        for model, cost in cost_by_model.items():
            if cost / total_cost > 0.6 and 'gpt-4' in model.lower():
                suggestions.append(
                    f"Consider using GPT-3.5-turbo for simpler tasks instead of {model} "
                    f"(accounts for {cost/total_cost*100:.1f}% of costs)"
                )
        
        # Check for high token usage
        avg_input = statistics.mean(call.input_tokens for call in calls)
        avg_output = statistics.mean(call.output_tokens for call in calls)
        
        if avg_input > 1000:
            suggestions.append(
                f"Average input tokens ({avg_input:.0f}) is high. "
                "Consider summarizing or chunking input context."
            )
        
        if avg_output > 1000:
            suggestions.append(
                f"Average output tokens ({avg_output:.0f}) is high. "
                "Consider using max_tokens limits or more focused prompts."
            )
        
        # Check for frequent calls
        if len(calls) > 100:
            suggestions.append(
                f"High call frequency ({len(calls)} calls). "
                "Consider caching responses or batching requests."
            )
        
        # Check for model variety
        if len(cost_by_model) > 3:
            suggestions.append(
                f"Using {len(cost_by_model)} different models. "
                "Standardizing on fewer models could reduce complexity and costs."
            )
        
        # Check for failed calls (if available)
        failed_calls = [call for call in calls if call.response == "" or "error" in call.metadata.get("status", "")]
        if failed_calls:
            suggestions.append(
                f"{len(failed_calls)} failed calls detected. "
                "Review error handling to avoid wasted tokens."
            )
        
        return suggestions
    
    def _get_llm_calls(self, graph_run_id: Optional[str] = None, 
                      time_period: Optional[Tuple[datetime, datetime]] = None) -> List[LLMCall]:
        """Get LLM calls from recorder"""
        if not self.recorder:
            return []
        
        # This would be implemented in the recorder
        # For now, return empty list
        return []
    
    def estimate_monthly_cost(self, days_sample: int = 7) -> Dict[str, Any]:
        """Estimate monthly costs based on recent usage"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_sample)
        
        calls = self._get_llm_calls(time_period=(start_time, end_time))
        
        if not calls:
            return {
                'estimated_monthly_cost': 0.0,
                'confidence': 'low',
                'sample_period_days': days_sample,
                'calls_in_sample': 0
            }
        
        # Calculate daily average
        daily_cost = sum(call.cost_usd for call in calls) / days_sample
        monthly_estimate = daily_cost * 30
        
        # Determine confidence based on sample size
        confidence = 'low'
        if len(calls) > 50:
            confidence = 'high'
        elif len(calls) > 20:
            confidence = 'medium'
        
        return {
            'estimated_monthly_cost': monthly_estimate,
            'daily_average_cost': daily_cost,
            'confidence': confidence,
            'sample_period_days': days_sample,
            'calls_in_sample': len(calls),
            'breakdown_by_model': self._get_model_breakdown(calls, monthly_estimate)
        }
    
    def _get_model_breakdown(self, calls: List[LLMCall], total_monthly: float) -> Dict[str, Dict[str, Any]]:
        """Get monthly cost breakdown by model"""
        model_costs = {}
        total_sample_cost = sum(call.cost_usd for call in calls)
        
        for call in calls:
            model = call.model_name
            if model not in model_costs:
                model_costs[model] = {'cost': 0, 'calls': 0}
            model_costs[model]['cost'] += call.cost_usd
            model_costs[model]['calls'] += 1
        
        # Scale to monthly estimates
        breakdown = {}
        for model, data in model_costs.items():
            sample_cost = data['cost']
            monthly_cost = (sample_cost / total_sample_cost) * total_monthly if total_sample_cost > 0 else 0
            breakdown[model] = {
                'estimated_monthly_cost': monthly_cost,
                'monthly_calls_estimate': data['calls'] * 30 / 7,  # Assuming 7-day sample
                'percentage_of_total': (monthly_cost / total_monthly * 100) if total_monthly > 0 else 0
            }
        
        return breakdown
