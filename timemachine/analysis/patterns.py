"""
Pattern Detection for TimeMachine
Identifies common issues, inefficiencies, and optimization opportunities
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from collections import Counter

from .llm_tracker import LLMCall


@dataclass
class Pattern:
    """Represents a detected pattern"""
    id: str
    name: str
    description: str
    severity: str  # low, medium, high, critical
    occurrences: int
    examples: List[str]
    suggestions: List[str]
    category: str  # cost, performance, reliability, quality
    confidence: float  # 0-1, how confident we are in this pattern


@dataclass
class PatternSummary:
    """Summary of all detected patterns"""
    total_patterns: int
    critical_issues: int
    high_priority: int
    medium_priority: int
    low_priority: int
    patterns_by_category: Dict[str, List[Pattern]]
    top_recommendations: List[str]


class PatternDetector:
    """Detects patterns and issues in LLM usage and agent behavior"""
    
    def __init__(self, recorder=None):
        self.recorder = recorder
        
    def detect_patterns(self, graph_run_id: Optional[str] = None,
                       time_period: Optional[Tuple[datetime, datetime]] = None) -> PatternSummary:
        """Detect all patterns in execution data"""
        
        # Get execution and LLM call data
        executions = self._get_executions(graph_run_id, time_period)
        llm_calls = self._get_llm_calls(graph_run_id, time_period)
        
        patterns = []
        
        # Cost-related patterns
        patterns.extend(self._detect_cost_patterns(llm_calls))
        
        # Performance patterns
        patterns.extend(self._detect_performance_patterns(executions, llm_calls))
        
        # Reliability patterns
        patterns.extend(self._detect_reliability_patterns(executions, llm_calls))
        
        # Quality patterns
        patterns.extend(self._detect_quality_patterns(llm_calls))
        
        return self._create_summary(patterns)
    
    def _detect_cost_patterns(self, llm_calls: List[LLMCall]) -> List[Pattern]:
        """Detect cost-related inefficiencies"""
        patterns = []
        
        if not llm_calls:
            return patterns
        
        # Pattern: Expensive model overuse
        expensive_models = ['gpt-4', 'claude-3-opus']
        expensive_calls = [call for call in llm_calls 
                          if any(model in call.model_name.lower() for model in expensive_models)]
        
        if len(expensive_calls) / len(llm_calls) > 0.7:
            patterns.append(Pattern(
                id="expensive_model_overuse",
                name="Expensive Model Overuse",
                description=f"{len(expensive_calls)}/{len(llm_calls)} calls use expensive models",
                severity="high",
                occurrences=len(expensive_calls),
                examples=[f"{call.model_name}: ${call.cost_usd:.3f}" for call in expensive_calls[:3]],
                suggestions=[
                    "Consider using GPT-3.5-turbo for simpler tasks",
                    "Reserve GPT-4 for complex reasoning only",
                    "Implement model routing based on task complexity"
                ],
                category="cost",
                confidence=0.9
            ))
        
        # Pattern: High token usage
        high_token_calls = [call for call in llm_calls if call.total_tokens > 2000]
        if len(high_token_calls) > len(llm_calls) * 0.3:
            patterns.append(Pattern(
                id="high_token_usage",
                name="High Token Usage",
                description=f"{len(high_token_calls)} calls use >2000 tokens",
                severity="medium",
                occurrences=len(high_token_calls),
                examples=[f"{call.total_tokens} tokens, ${call.cost_usd:.3f}" for call in high_token_calls[:3]],
                suggestions=[
                    "Implement input summarization",
                    "Use more focused prompts",
                    "Consider chunking large inputs"
                ],
                category="cost",
                confidence=0.8
            ))
        
        # Pattern: Repeated similar prompts (potential caching opportunity)
        prompt_similarity = self._detect_similar_prompts(llm_calls)
        if prompt_similarity['high_similarity_count'] > 5:
            patterns.append(Pattern(
                id="repeated_prompts",
                name="Repeated Similar Prompts",
                description=f"{prompt_similarity['high_similarity_count']} similar prompts detected",
                severity="medium",
                occurrences=prompt_similarity['high_similarity_count'],
                examples=prompt_similarity['examples'],
                suggestions=[
                    "Implement response caching for similar prompts",
                    "Use prompt templates to standardize inputs",
                    "Consider batching similar requests"
                ],
                category="cost",
                confidence=0.7
            ))
        
        return patterns
    
    def _detect_performance_patterns(self, executions: List[Dict], llm_calls: List[LLMCall]) -> List[Pattern]:
        """Detect performance-related issues"""
        patterns = []
        
        if not executions:
            return patterns
        
        # Pattern: Slow node executions
        slow_executions = [exec for exec in executions 
                          if exec.get('duration_ms', 0) > 5000]  # >5 seconds
        
        if len(slow_executions) > len(executions) * 0.2:
            patterns.append(Pattern(
                id="slow_executions",
                name="Slow Node Executions",
                description=f"{len(slow_executions)} nodes took >5 seconds",
                severity="high",
                occurrences=len(slow_executions),
                examples=[f"{exec.get('node_name', 'unknown')}: {exec.get('duration_ms', 0)}ms" 
                         for exec in slow_executions[:3]],
                suggestions=[
                    "Optimize slow nodes",
                    "Consider parallel execution",
                    "Review LLM response times",
                    "Implement timeouts"
                ],
                category="performance",
                confidence=0.9
            ))
        
        # Pattern: Sequential LLM calls that could be parallel
        sequential_calls = self._detect_sequential_calls(llm_calls)
        if sequential_calls['count'] > 3:
            patterns.append(Pattern(
                id="sequential_llm_calls",
                name="Sequential LLM Calls",
                description=f"{sequential_calls['count']} LLM calls could be parallelized",
                severity="medium",
                occurrences=sequential_calls['count'],
                examples=sequential_calls['examples'],
                suggestions=[
                    "Implement parallel LLM calls where possible",
                    "Batch independent requests",
                    "Review node dependencies"
                ],
                category="performance",
                confidence=0.6
            ))
        
        return patterns
    
    def _detect_reliability_patterns(self, executions: List[Dict], llm_calls: List[LLMCall]) -> List[Pattern]:
        """Detect reliability issues"""
        patterns = []
        
        if not executions:
            return patterns
        
        # Pattern: High error rate
        failed_executions = [exec for exec in executions 
                           if exec.get('status') == 'error']
        
        if len(failed_executions) > len(executions) * 0.1:
            patterns.append(Pattern(
                id="high_error_rate",
                name="High Error Rate",
                description=f"{len(failed_executions)}/{len(executions)} executions failed",
                severity="critical",
                occurrences=len(failed_executions),
                examples=[exec.get('error_message', 'Unknown error')[:100] 
                         for exec in failed_executions[:3]],
                suggestions=[
                    "Review error handling logic",
                    "Add retry mechanisms",
                    "Implement input validation",
                    "Add fallback strategies"
                ],
                category="reliability",
                confidence=0.95
            ))
        
        # Pattern: Inconsistent outputs for similar inputs
        output_inconsistency = self._detect_output_inconsistency(llm_calls)
        if output_inconsistency['score'] > 0.7:
            patterns.append(Pattern(
                id="inconsistent_outputs",
                name="Inconsistent LLM Outputs",
                description="High variance in outputs for similar inputs",
                severity="medium",
                occurrences=output_inconsistency['examples_count'],
                examples=output_inconsistency['examples'],
                suggestions=[
                    "Lower temperature for more consistent outputs",
                    "Use system prompts for consistency",
                    "Implement output validation",
                    "Consider deterministic model settings"
                ],
                category="reliability",
                confidence=0.6
            ))
        
        return patterns
    
    def _detect_quality_patterns(self, llm_calls: List[LLMCall]) -> List[Pattern]:
        """Detect quality issues in LLM interactions"""
        patterns = []
        
        if not llm_calls:
            return patterns
        
        # Pattern: Short responses (might indicate poor prompting)
        short_responses = [call for call in llm_calls 
                          if call.output_tokens < 10 and call.input_tokens > 100]
        
        if len(short_responses) > len(llm_calls) * 0.3:
            patterns.append(Pattern(
                id="short_responses",
                name="Unexpectedly Short Responses",
                description=f"{len(short_responses)} calls produced very short outputs",
                severity="medium",
                occurrences=len(short_responses),
                examples=[f"Input: {call.input_tokens}t → Output: {call.output_tokens}t" 
                         for call in short_responses[:3]],
                suggestions=[
                    "Review prompt clarity and specificity",
                    "Add examples to prompts",
                    "Check if model understands the task",
                    "Consider using more detailed instructions"
                ],
                category="quality",
                confidence=0.7
            ))
        
        # Pattern: High rejection/refusal rates
        refusal_indicators = ['cannot', "can't", 'unable', 'sorry', 'apologize', 'refuse']
        refusal_calls = []
        for call in llm_calls:
            if any(indicator in call.response.lower() for indicator in refusal_indicators):
                refusal_calls.append(call)
        
        if len(refusal_calls) > len(llm_calls) * 0.2:
            patterns.append(Pattern(
                id="high_refusal_rate",
                name="High LLM Refusal Rate",
                description=f"{len(refusal_calls)} calls resulted in refusals or apologies",
                severity="high",
                occurrences=len(refusal_calls),
                examples=[call.response[:100] + "..." for call in refusal_calls[:3]],
                suggestions=[
                    "Review prompts for clarity and appropriateness",
                    "Check content policy compliance",
                    "Rephrase requests to be more specific",
                    "Consider alternative models or approaches"
                ],
                category="quality",
                confidence=0.8
            ))
        
        return patterns
    
    def _detect_similar_prompts(self, llm_calls: List[LLMCall]) -> Dict[str, Any]:
        """Detect similar prompts that could benefit from caching"""
        if len(llm_calls) < 2:
            return {'high_similarity_count': 0, 'examples': []}
        
        similar_groups = []
        processed = set()
        
        for i, call1 in enumerate(llm_calls):
            if i in processed:
                continue
                
            group = [call1]
            for j, call2 in enumerate(llm_calls[i+1:], i+1):
                if j in processed:
                    continue
                    
                similarity = self._calculate_prompt_similarity(call1.prompt, call2.prompt)
                if similarity > 0.8:  # High similarity threshold
                    group.append(call2)
                    processed.add(j)
            
            if len(group) > 1:
                similar_groups.append(group)
                processed.add(i)
        
        high_similarity_count = sum(len(group) for group in similar_groups)
        examples = []
        for group in similar_groups[:3]:
            examples.append(f"Group of {len(group)} similar prompts: '{group[0].prompt[:50]}...'")
        
        return {
            'high_similarity_count': high_similarity_count,
            'examples': examples,
            'groups': similar_groups
        }
    
    def _calculate_prompt_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate similarity between two prompts (simple approach)"""
        if not prompt1 or not prompt2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_sequential_calls(self, llm_calls: List[LLMCall]) -> Dict[str, Any]:
        """Detect sequential calls that could be parallelized"""
        if len(llm_calls) < 2:
            return {'count': 0, 'examples': []}
        
        # Sort by timestamp
        sorted_calls = sorted(llm_calls, key=lambda x: x.timestamp)
        
        sequential_groups = []
        current_group = [sorted_calls[0]]
        
        for i in range(1, len(sorted_calls)):
            prev_call = sorted_calls[i-1]
            curr_call = sorted_calls[i]
            
            # If calls are within 1 second and don't depend on each other
            time_diff = curr_call.timestamp - prev_call.timestamp
            if time_diff < 1.0 and not self._calls_are_dependent(prev_call, curr_call):
                current_group.append(curr_call)
            else:
                if len(current_group) > 1:
                    sequential_groups.append(current_group)
                current_group = [curr_call]
        
        if len(current_group) > 1:
            sequential_groups.append(current_group)
        
        count = sum(len(group) for group in sequential_groups)
        examples = [f"Group of {len(group)} sequential calls" for group in sequential_groups[:3]]
        
        return {'count': count, 'examples': examples}
    
    def _calls_are_dependent(self, call1: LLMCall, call2: LLMCall) -> bool:
        """Check if call2 depends on output from call1"""
        # Simple heuristic: if call2's prompt contains words from call1's response
        if not call1.response or not call2.prompt:
            return False
        
        response_words = set(call1.response.lower().split())
        prompt_words = set(call2.prompt.lower().split())
        
        # If more than 20% of response words appear in the next prompt
        overlap = len(response_words.intersection(prompt_words))
        return overlap / len(response_words) > 0.2 if response_words else False
    
    def _detect_output_inconsistency(self, llm_calls: List[LLMCall]) -> Dict[str, Any]:
        """Detect inconsistent outputs for similar inputs"""
        if len(llm_calls) < 3:
            return {'score': 0.0, 'examples_count': 0, 'examples': []}
        
        similar_groups = self._detect_similar_prompts(llm_calls)['groups']
        inconsistent_examples = []
        
        for group in similar_groups:
            if len(group) < 2:
                continue
                
            # Check response diversity within the group
            responses = [call.response for call in group]
            diversity_score = self._calculate_response_diversity(responses)
            
            if diversity_score > 0.7:  # High diversity for similar prompts
                inconsistent_examples.append({
                    'prompt': group[0].prompt[:50] + "...",
                    'responses': [resp[:30] + "..." for resp in responses[:3]],
                    'diversity': diversity_score
                })
        
        avg_inconsistency = sum(ex['diversity'] for ex in inconsistent_examples) / len(inconsistent_examples) if inconsistent_examples else 0.0
        
        return {
            'score': avg_inconsistency,
            'examples_count': len(inconsistent_examples),
            'examples': [f"Prompt: {ex['prompt']} → Various responses" for ex in inconsistent_examples[:3]]
        }
    
    def _calculate_response_diversity(self, responses: List[str]) -> float:
        """Calculate diversity score for a set of responses"""
        if len(responses) < 2:
            return 0.0
        
        similarities = []
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                sim = self._calculate_prompt_similarity(responses[i], responses[j])
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities)
        return 1.0 - avg_similarity  # High diversity = low similarity
    
    def _create_summary(self, patterns: List[Pattern]) -> PatternSummary:
        """Create summary of detected patterns"""
        severity_counts = Counter(pattern.severity for pattern in patterns)
        category_patterns = {}
        
        for pattern in patterns:
            if pattern.category not in category_patterns:
                category_patterns[pattern.category] = []
            category_patterns[pattern.category].append(pattern)
        
        # Generate top recommendations
        top_recommendations = []
        for pattern in sorted(patterns, key=lambda x: (x.severity == 'critical', x.severity == 'high', x.confidence), reverse=True)[:5]:
            if pattern.suggestions:
                top_recommendations.append(f"{pattern.name}: {pattern.suggestions[0]}")
        
        return PatternSummary(
            total_patterns=len(patterns),
            critical_issues=severity_counts.get('critical', 0),
            high_priority=severity_counts.get('high', 0),
            medium_priority=severity_counts.get('medium', 0),
            low_priority=severity_counts.get('low', 0),
            patterns_by_category=category_patterns,
            top_recommendations=top_recommendations
        )
    
    def _get_executions(self, graph_run_id: Optional[str] = None,
                       time_period: Optional[Tuple[datetime, datetime]] = None) -> List[Dict]:
        """Get execution data from recorder"""
        if not self.recorder:
            return []
        # This would be implemented in the recorder
        return []
    
    def _get_llm_calls(self, graph_run_id: Optional[str] = None,
                      time_period: Optional[Tuple[datetime, datetime]] = None) -> List[LLMCall]:
        """Get LLM call data"""
        if not self.recorder:
            return []
        # This would be implemented in the recorder
        return []
