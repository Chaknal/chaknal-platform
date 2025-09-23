#!/usr/bin/env python3
"""
Chaknal Platform Performance and Scaling Test
Tests the platform under load and measures performance
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import json

# Configuration
BACKEND_URL = "https://chaknal-backend-container.azurewebsites.net"
FRONTEND_URL = "https://agreeable-bush-01890e00f.1.azurestaticapps.net"

class PerformanceTest:
    def __init__(self):
        self.results = []
        self.errors = []
        
    def single_request_test(self, url, method="GET", headers=None, data=None):
        """Test a single request and measure performance"""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "url": url,
                "method": method
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "url": url,
                "method": method
            }
    
    def load_test(self, url, concurrent_requests=10, total_requests=50):
        """Run load test with multiple concurrent requests"""
        print(f"🚀 Running load test: {concurrent_requests} concurrent, {total_requests} total requests")
        
        results = []
        errors = []
        
        def worker():
            for _ in range(total_requests // concurrent_requests):
                result = self.single_request_test(url)
                if result["success"]:
                    results.append(result)
                else:
                    errors.append(result)
                time.sleep(0.1)  # Small delay between requests
        
        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_requests):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        if results:
            response_times = [r["response_time"] for r in results]
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            success_rate = len(results) / (len(results) + len(errors)) * 100
            requests_per_second = len(results) / total_time
            
            return {
                "total_requests": len(results) + len(errors),
                "successful_requests": len(results),
                "failed_requests": len(errors),
                "success_rate": success_rate,
                "total_time": total_time,
                "requests_per_second": requests_per_second,
                "avg_response_time": avg_response_time,
                "median_response_time": median_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "p95_response_time": p95_response_time,
                "errors": errors[:5]  # First 5 errors for debugging
            }
        else:
            return {
                "total_requests": len(errors),
                "successful_requests": 0,
                "failed_requests": len(errors),
                "success_rate": 0,
                "errors": errors[:5]
            }
    
    def test_endpoints(self):
        """Test various endpoints for performance"""
        endpoints = [
            {"url": f"{BACKEND_URL}/health", "method": "GET", "name": "Health Check"},
            {"url": f"{BACKEND_URL}/api/duxsoup-users/", "method": "GET", "name": "DuxSoup Users API"},
            {"url": f"{BACKEND_URL}/api/version", "method": "GET", "name": "Version API"},
            {"url": f"{BACKEND_URL}/api/auth/status", "method": "GET", "name": "Auth Status API"},
            {"url": f"{FRONTEND_URL}/", "method": "GET", "name": "Frontend Home"},
            {"url": f"{BACKEND_URL}/docs", "method": "GET", "name": "API Documentation"}
        ]
        
        print("🧪 Testing individual endpoints...")
        for endpoint in endpoints:
            print(f"\n   Testing {endpoint['name']}:")
            result = self.single_request_test(endpoint["url"], endpoint["method"])
            
            if result["success"]:
                print(f"   ✅ {result['response_time']:.2f}ms (HTTP {result['status_code']})")
            else:
                print(f"   ❌ Failed: {result['error']}")
    
    def run_comprehensive_test(self):
        """Run comprehensive performance and scaling test"""
        print("🔍 Chaknal Platform Performance Test")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Test individual endpoints
        self.test_endpoints()
        
        # Run load tests
        print("\n📊 Load Testing...")
        
        # Test health endpoint under load
        print("\n🏥 Health Endpoint Load Test:")
        health_results = self.load_test(f"{BACKEND_URL}/health", concurrent_requests=5, total_requests=25)
        self.print_load_test_results(health_results)
        
        # Test API endpoint under load
        print("\n🔌 API Endpoint Load Test:")
        api_results = self.load_test(f"{BACKEND_URL}/api/duxsoup-users/", concurrent_requests=3, total_requests=15)
        self.print_load_test_results(api_results)
        
        # Test frontend under load
        print("\n🌐 Frontend Load Test:")
        frontend_results = self.load_test(f"{FRONTEND_URL}/", concurrent_requests=5, total_requests=25)
        self.print_load_test_results(frontend_results)
        
        # Performance recommendations
        self.print_recommendations(health_results, api_results, frontend_results)
    
    def print_load_test_results(self, results):
        """Print load test results in a formatted way"""
        if results["successful_requests"] > 0:
            print(f"   ✅ Success Rate: {results['success_rate']:.1f}%")
            print(f"   ⚡ Requests/sec: {results['requests_per_second']:.2f}")
            print(f"   ⏱️  Avg Response: {results['avg_response_time']:.2f}ms")
            print(f"   📊 Median Response: {results['median_response_time']:.2f}ms")
            print(f"   🎯 P95 Response: {results['p95_response_time']:.2f}ms")
            print(f"   📈 Min/Max: {results['min_response_time']:.2f}ms / {results['max_response_time']:.2f}ms")
        else:
            print(f"   ❌ All requests failed")
            if results.get("errors"):
                print(f"   Error sample: {results['errors'][0]['error']}")
    
    def print_recommendations(self, health_results, api_results, frontend_results):
        """Print performance recommendations based on test results"""
        print("\n💡 Performance Recommendations:")
        print("=" * 40)
        
        # Check response times
        all_results = [health_results, api_results, frontend_results]
        avg_response_times = [r.get("avg_response_time", 0) for r in all_results if r.get("successful_requests", 0) > 0]
        
        if avg_response_times:
            max_avg_response = max(avg_response_times)
            if max_avg_response > 2000:  # 2 seconds
                print("⚠️  High response times detected. Consider:")
                print("   - Enabling CDN for static content")
                print("   - Optimizing database queries")
                print("   - Implementing caching")
            elif max_avg_response > 1000:  # 1 second
                print("⚠️  Moderate response times. Consider:")
                print("   - Database query optimization")
                print("   - Response compression")
            else:
                print("✅ Response times are good!")
        
        # Check success rates
        success_rates = [r.get("success_rate", 0) for r in all_results]
        min_success_rate = min(success_rates) if success_rates else 0
        
        if min_success_rate < 95:
            print("⚠️  Low success rates detected. Consider:")
            print("   - Increasing App Service instance count")
            print("   - Implementing retry logic")
            print("   - Adding circuit breakers")
        else:
            print("✅ Success rates are excellent!")
        
        # Check requests per second
        rps_values = [r.get("requests_per_second", 0) for r in all_results if r.get("successful_requests", 0) > 0]
        if rps_values:
            max_rps = max(rps_values)
            if max_rps < 10:
                print("⚠️  Low throughput detected. Consider:")
                print("   - Scaling up App Service plan")
                print("   - Implementing horizontal scaling")
                print("   - Optimizing application code")
            else:
                print("✅ Throughput is good!")
        
        print("\n🚀 Scaling Recommendations:")
        print("   - Current setup supports moderate traffic")
        print("   - Consider upgrading to Premium plan for high availability")
        print("   - Implement auto-scaling rules for traffic spikes")
        print("   - Set up monitoring alerts for performance degradation")

def main():
    """Main function"""
    test = PerformanceTest()
    test.run_comprehensive_test()

if __name__ == "__main__":
    main()
