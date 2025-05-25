#!/usr/bin/env python3
"""Benchmark script to compare performance before and after optimizations"""

import time
import json
import statistics
from typing import List, Dict, Any
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Test configuration
BASE_URL = "http://localhost:5003"
NUM_REQUESTS = 100
CONCURRENT_REQUESTS = 10


def generate_test_payload() -> Dict[str, Any]:
    """Generate a test webhook payload"""
    return {
        "eventEnum": "RECALCULATE_ACTION_PLAN",
        "eventPayload": json.dumps({
            "actionPlanUniqueId": "test-plan-123",
            "accountId": 494,
            "pillarCompletionStats": [
                {
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [
                        {
                            "routineId": i,
                            "displayName": f"Routine {i}",
                            "completionStatistics": [
                                {
                                    "completionRate": 3,
                                    "completionRatePeriodUnit": "WEEK",
                                    "periodSequenceNo": 1
                                }
                            ]
                        } for i in range(1, 11)  # 10 routines per pillar
                    ]
                } for pillar in ["STRESS", "MOVEMENT", "NUTRITION", "SLEEP"]
            ]
        })
    }


def benchmark_endpoint(endpoint: str, payload: Dict, num_requests: int) -> Dict[str, float]:
    """Benchmark a single endpoint"""
    response_times = []
    errors = 0
    
    print(f"\nBenchmarking {endpoint}...")
    
    start_time = time.time()
    
    def make_request():
        try:
            req_start = time.time()
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
            req_time = time.time() - req_start
            
            if response.status_code >= 400:
                return None, req_time
            return response.status_code, req_time
        except Exception as e:
            return None, 0
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        
        for future in as_completed(futures):
            status, req_time = future.result()
            if status is None:
                errors += 1
            else:
                response_times.append(req_time * 1000)  # Convert to ms
    
    total_time = time.time() - start_time
    
    if response_times:
        return {
            'total_requests': num_requests,
            'successful_requests': len(response_times),
            'errors': errors,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p50_response_time': statistics.median(response_times),
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
            'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
        }
    else:
        return {'errors': errors, 'total_requests': num_requests}


def print_results(endpoint: str, results: Dict[str, float]):
    """Print benchmark results"""
    print(f"\n{'='*60}")
    print(f"Results for {endpoint}")
    print(f"{'='*60}")
    print(f"Total Requests: {results.get('total_requests', 0)}")
    print(f"Successful: {results.get('successful_requests', 0)}")
    print(f"Errors: {results.get('errors', 0)}")
    print(f"Total Time: {results.get('total_time', 0):.2f}s")
    print(f"Requests/Second: {results.get('requests_per_second', 0):.2f}")
    print(f"\nResponse Times (ms):")
    print(f"  Average: {results.get('avg_response_time', 0):.2f}")
    print(f"  Min: {results.get('min_response_time', 0):.2f}")
    print(f"  Max: {results.get('max_response_time', 0):.2f}")
    print(f"  P50: {results.get('p50_response_time', 0):.2f}")
    print(f"  P95: {results.get('p95_response_time', 0):.2f}")
    print(f"  P99: {results.get('p99_response_time', 0):.2f}")


def compare_performance():
    """Compare performance between original and optimized endpoints"""
    payload = generate_test_payload()
    
    # Test original endpoint
    original_results = benchmark_endpoint("/event", payload, NUM_REQUESTS)
    print_results("Original /event", original_results)
    
    # Test optimized webhook (if implemented)
    try:
        optimized_results = benchmark_endpoint("/webhook/optimized", 
                                             {"test": "data"}, 
                                             NUM_REQUESTS)
        print_results("Optimized /webhook", optimized_results)
        
        # Calculate improvement
        if 'avg_response_time' in original_results and 'avg_response_time' in optimized_results:
            improvement = (
                (original_results['avg_response_time'] - optimized_results['avg_response_time']) 
                / original_results['avg_response_time'] * 100
            )
            print(f"\n🚀 Performance Improvement: {improvement:.1f}%")
    except:
        print("\nOptimized endpoint not available")


if __name__ == "__main__":
    print("Performance Benchmark Tool")
    print("="*60)
    print(f"Target: {BASE_URL}")
    print(f"Requests: {NUM_REQUESTS}")
    print(f"Concurrent: {CONCURRENT_REQUESTS}")
    
    compare_performance()