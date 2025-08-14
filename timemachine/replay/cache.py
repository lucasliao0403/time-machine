"""
Response Cache for TimeMachine
Caches LLM responses to enable faster and cheaper replays
"""
import hashlib
import json
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CachedResponse:
    """Represents a cached LLM response"""
    cache_key: str
    model_name: str
    prompt_hash: str
    parameters_hash: str
    response: str
    tokens_used: int
    cost_saved: float
    timestamp: float
    hit_count: int


class ResponseCache:
    """Caches LLM responses for replay scenarios"""
    
    def __init__(self, cache_db_path: str = "timemachine_cache.db"):
        self.cache_db_path = cache_db_path
        self.init_cache_database()
        
    def init_cache_database(self):
        """Initialize cache database"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS response_cache (
                    cache_key TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    parameters_hash TEXT NOT NULL,
                    response TEXT NOT NULL,
                    tokens_used INTEGER,
                    cost_saved REAL DEFAULT 0.0,
                    timestamp REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    expires_at REAL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_model_prompt 
                ON response_cache(model_name, prompt_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_timestamp 
                ON response_cache(timestamp)
            """)
            
            conn.commit()
    
    def generate_cache_key(self, model_name: str, prompt: str, 
                          parameters: Dict[str, Any]) -> str:
        """Generate a unique cache key for the request"""
        # Create a stable hash from prompt and parameters
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
        
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(parameters, sort_keys=True)
        params_hash = hashlib.sha256(sorted_params.encode('utf-8')).hexdigest()[:16]
        
        return f"{model_name}:{prompt_hash}:{params_hash}"
    
    def get_cached_response(self, model_name: str, prompt: str, 
                           parameters: Dict[str, Any]) -> Optional[CachedResponse]:
        """Get cached response if available"""
        cache_key = self.generate_cache_key(model_name, prompt, parameters)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT cache_key, model_name, prompt_hash, parameters_hash, 
                       response, tokens_used, cost_saved, timestamp, hit_count
                FROM response_cache 
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > ?)
            """, (cache_key, time.time()))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Update hit count
            conn.execute("""
                UPDATE response_cache 
                SET hit_count = hit_count + 1 
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()
            
            return CachedResponse(
                cache_key=row[0],
                model_name=row[1],
                prompt_hash=row[2],
                parameters_hash=row[3],
                response=row[4],
                tokens_used=row[5] or 0,
                cost_saved=row[6] or 0.0,
                timestamp=row[7],
                hit_count=row[8] + 1
            )
    
    def cache_response(self, model_name: str, prompt: str, parameters: Dict[str, Any],
                      response: str, tokens_used: int = 0, cost: float = 0.0,
                      ttl_hours: Optional[int] = None) -> str:
        """Cache an LLM response"""
        cache_key = self.generate_cache_key(model_name, prompt, parameters)
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
        params_hash = hashlib.sha256(
            json.dumps(parameters, sort_keys=True).encode('utf-8')
        ).hexdigest()[:16]
        
        expires_at = None
        if ttl_hours:
            expires_at = time.time() + (ttl_hours * 3600)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO response_cache 
                (cache_key, model_name, prompt_hash, parameters_hash, response, 
                 tokens_used, cost_saved, timestamp, hit_count, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (cache_key, model_name, prompt_hash, params_hash, response,
                  tokens_used, cost, time.time(), expires_at))
            conn.commit()
        
        return cache_key
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with sqlite3.connect(self.cache_db_path) as conn:
            # Total entries
            total_entries = conn.execute("SELECT COUNT(*) FROM response_cache").fetchone()[0]
            
            # Total hits
            total_hits = conn.execute("SELECT SUM(hit_count) FROM response_cache").fetchone()[0] or 0
            
            # Total cost saved
            total_cost_saved = conn.execute("SELECT SUM(cost_saved * hit_count) FROM response_cache").fetchone()[0] or 0.0
            
            # Hit rate calculation
            total_requests = total_entries + total_hits
            hit_rate = (total_hits / total_requests) * 100 if total_requests > 0 else 0
            
            # Models cached
            models = conn.execute("SELECT DISTINCT model_name FROM response_cache").fetchall()
            models_list = [row[0] for row in models]
            
            # Cache size (approximate)
            cache_size_mb = conn.execute("""
                SELECT SUM(LENGTH(response) + LENGTH(cache_key) + LENGTH(model_name)) 
                FROM response_cache
            """).fetchone()[0] or 0
            cache_size_mb = cache_size_mb / (1024 * 1024)  # Convert to MB
            
            # Most frequently used
            frequent_entries = conn.execute("""
                SELECT model_name, hit_count, cost_saved * hit_count as total_saved
                FROM response_cache 
                ORDER BY hit_count DESC 
                LIMIT 5
            """).fetchall()
            
            return {
                'total_entries': total_entries,
                'total_hits': total_hits,
                'hit_rate_percent': round(hit_rate, 2),
                'total_cost_saved': round(total_cost_saved, 4),
                'models_cached': models_list,
                'cache_size_mb': round(cache_size_mb, 2),
                'most_frequent': [
                    {
                        'model': row[0], 
                        'hits': row[1], 
                        'cost_saved': round(row[2], 4)
                    } for row in frequent_entries
                ]
            }
    
    def clean_expired_entries(self) -> int:
        """Remove expired cache entries"""
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM response_cache 
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (time.time(),))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
    
    def clean_old_entries(self, keep_days: int = 30) -> int:
        """Remove entries older than specified days"""
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM response_cache 
                WHERE timestamp < ? AND hit_count = 0
            """, (cutoff_time,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
    
    def clear_cache(self) -> int:
        """Clear all cache entries"""
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("DELETE FROM response_cache")
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
    
    def get_similar_cached_responses(self, model_name: str, prompt: str, 
                                   similarity_threshold: float = 0.8) -> List[CachedResponse]:
        """Find cached responses with similar prompts"""
        # This is a simplified version - in practice, you'd use more sophisticated
        # similarity matching (e.g., embedding similarity)
        
        prompt_words = set(prompt.lower().split())
        
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT cache_key, model_name, prompt_hash, parameters_hash, 
                       response, tokens_used, cost_saved, timestamp, hit_count
                FROM response_cache 
                WHERE model_name = ?
            """, (model_name,))
            
            similar_responses = []
            for row in cursor.fetchall():
                # This would require storing the original prompt or using embeddings
                # For now, we'll return a simplified result
                cached_response = CachedResponse(
                    cache_key=row[0],
                    model_name=row[1],
                    prompt_hash=row[2],
                    parameters_hash=row[3],
                    response=row[4],
                    tokens_used=row[5] or 0,
                    cost_saved=row[6] or 0.0,
                    timestamp=row[7],
                    hit_count=row[8]
                )
                similar_responses.append(cached_response)
        
        return similar_responses[:10]  # Return top 10
    
    def warmup_cache(self, common_prompts: List[Dict[str, Any]]):
        """Pre-populate cache with common prompts"""
        # This would be used to pre-cache frequently used prompts
        # Implementation would depend on having access to LLM APIs
        pass
    
    def export_cache(self, file_path: str):
        """Export cache to JSON file"""
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT cache_key, model_name, response, tokens_used, 
                       cost_saved, timestamp, hit_count
                FROM response_cache
            """)
            
            cache_data = []
            for row in cursor.fetchall():
                cache_data.append({
                    'cache_key': row[0],
                    'model_name': row[1],
                    'response': row[2],
                    'tokens_used': row[3],
                    'cost_saved': row[4],
                    'timestamp': row[5],
                    'hit_count': row[6]
                })
        
        with open(file_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def import_cache(self, file_path: str):
        """Import cache from JSON file"""
        with open(file_path, 'r') as f:
            cache_data = json.load(f)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            for entry in cache_data:
                conn.execute("""
                    INSERT OR REPLACE INTO response_cache 
                    (cache_key, model_name, response, tokens_used, 
                     cost_saved, timestamp, hit_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry['cache_key'],
                    entry['model_name'], 
                    entry['response'],
                    entry['tokens_used'],
                    entry['cost_saved'],
                    entry['timestamp'],
                    entry['hit_count']
                ))
            conn.commit()
