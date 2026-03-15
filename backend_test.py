#!/usr/bin/env python3
"""
Backend Testing for PHASE 47-48: Research Analytics API Layer
=============================================================

Tests the unified backend analytics layer for chart visualization:
- PHASE 47: Modularity & Isolation Audit (providers, contracts, services)
- PHASE 48: Research Analytics API Layer

Endpoints to test:
1. GET /api/health - system health
2. GET /api/v1/research-analytics/health - PHASE 48 module health
3. GET /api/v1/research-analytics/chart-data/BTCUSDT/1h - chart data with mock candles
4. GET /api/v1/research-analytics/full-payload/BTCUSDT/1h - complete chart payload
5. GET /api/v1/research-analytics/suggestions/BTCUSDT/1h - regime detection and suggestions
6. GET /api/v1/research-analytics/fractal-matches/BTCUSDT/1h - fractal pattern matching
7. GET /api/v1/research-analytics/patterns/BTCUSDT/1h - pattern detection
8. GET /api/v1/research-analytics/hypothesis/BTCUSDT/1h - hypothesis visualization
9. GET /api/v1/research-analytics/presets - research presets list
"""

import requests
import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class ResearchAnalyticsAPITester:
    def __init__(self, base_url: str = "https://ta-detector-preview.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []
        
        print("=" * 80)
        print("PHASE 47-48 Research Analytics API Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Testing Time: {datetime.now(timezone.utc).isoformat()}")
        print()

    def log_test(self, name: str, passed: bool, details: str = "", data: Dict = None):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test_name": name,
            "passed": passed,
            "details": details,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.results.append(result)
        
        print(f"{status} | {name}")
        if details:
            print(f"      {details}")
        if data and not passed:
            print(f"      Error: {data.get('error', 'Unknown error')}")
        print()

    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200,
                     validate_data: callable = None, test_name: str = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        test_name = test_name or f"{method} {endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=30)
            else:
                self.log_test(test_name, False, f"Unsupported method: {method}")
                return {"success": False}
            
            # Check status code
            if response.status_code != expected_status:
                self.log_test(
                    test_name, False,
                    f"Expected {expected_status}, got {response.status_code}",
                    {"error": f"HTTP {response.status_code}", "response": response.text[:200]}
                )
                return {"success": False}
            
            # Parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                self.log_test(test_name, False, "Invalid JSON response")
                return {"success": False}
            
            # Custom validation
            if validate_data and not validate_data(data):
                self.log_test(test_name, False, "Data validation failed", data)
                return {"success": False}
            
            self.log_test(test_name, True, f"Status: {response.status_code}", data)
            return {"success": True, "data": data}
            
        except requests.RequestException as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
            return {"success": False}

    def validate_health_response(self, data: Dict) -> bool:
        """Validate health endpoint response"""
        required_fields = ["ok", "version", "phase", "timestamp"]
        return all(field in data for field in required_fields) and data.get("ok") is True

    def validate_research_health(self, data: Dict) -> bool:
        """Validate research analytics health response"""
        return (
            data.get("status") == "ok" and
            data.get("phase") == "48" and
            data.get("module") == "research_analytics" and
            "components" in data and
            isinstance(data["components"], dict)
        )

    def validate_chart_data(self, data: Dict) -> bool:
        """Validate chart data response"""
        required_fields = ["symbol", "timeframe", "timestamp", "candles"]
        if not all(field in data for field in required_fields):
            return False
        
        # Check candles structure
        if not isinstance(data["candles"], list) or len(data["candles"]) == 0:
            return False
        
        # Validate first candle structure
        candle = data["candles"][0]
        candle_fields = ["timestamp", "open", "high", "low", "close", "volume"]
        return all(field in candle for field in candle_fields)

    def validate_full_payload(self, data: Dict) -> bool:
        """Validate full chart payload response"""
        required_fields = ["symbol", "timeframe", "timestamp", "candles"]
        if not all(field in data for field in required_fields):
            return False
        
        # Should have suggestions and regime
        if "regime" not in data or "suggested_indicators" not in data:
            return False
        
        return len(data["candles"]) > 0

    def validate_suggestions(self, data: Dict) -> bool:
        """Validate suggestions response"""
        required_fields = ["regime", "confidence", "suggested_indicators", "suggested_overlays"]
        return all(field in data for field in required_fields)

    def validate_fractal_matches(self, data: Dict) -> bool:
        """Validate fractal matches response"""
        required_fields = ["symbol", "timeframe", "scan_timestamp", "matches"]
        return all(field in data for field in required_fields) and isinstance(data["matches"], list)

    def validate_patterns(self, data: Dict) -> bool:
        """Validate patterns response"""
        required_fields = ["symbol", "timeframe", "patterns", "count"]
        return all(field in data for field in required_fields) and isinstance(data["patterns"], list)

    def validate_hypothesis(self, data: Dict) -> bool:
        """Validate hypothesis visualization response"""
        required_fields = ["hypothesis_id", "symbol", "timeframe", "direction", "confidence"]
        return all(field in data for field in required_fields)

    def validate_presets(self, data: Dict) -> bool:
        """Validate presets response"""
        required_fields = ["presets", "count"]
        return all(field in data for field in required_fields) and isinstance(data["presets"], list)

    def run_all_tests(self):
        """Run all tests"""
        print("Starting comprehensive API testing...")
        print()
        
        # Test 1: System Health
        self.test_endpoint(
            "GET", "/api/health",
            validate_data=self.validate_health_response,
            test_name="System Health Check"
        )
        
        # Test 2: Research Analytics Module Health
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/health",
            validate_data=self.validate_research_health,
            test_name="Research Analytics Health Check"
        )
        
        # Test 3: Chart Data API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/chart-data/BTCUSDT/1h",
            validate_data=self.validate_chart_data,
            test_name="Chart Data API (BTCUSDT/1h)"
        )
        
        # Test 4: Full Payload API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/full-payload/BTCUSDT/1h",
            validate_data=self.validate_full_payload,
            test_name="Full Chart Payload API"
        )
        
        # Test 5: Suggestions API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/suggestions/BTCUSDT/1h",
            validate_data=self.validate_suggestions,
            test_name="Chart Suggestions API"
        )
        
        # Test 6: Fractal Matches API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/fractal-matches/BTCUSDT/1h",
            validate_data=self.validate_fractal_matches,
            test_name="Fractal Pattern Matching API"
        )
        
        # Test 7: Patterns API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/patterns/BTCUSDT/1h",
            validate_data=self.validate_patterns,
            test_name="Pattern Detection API"
        )
        
        # Test 8: Hypothesis Visualization API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/hypothesis/BTCUSDT/1h",
            validate_data=self.validate_hypothesis,
            test_name="Hypothesis Visualization API"
        )
        
        # Test 9: Research Presets API
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/presets",
            validate_data=self.validate_presets,
            test_name="Research Presets API"
        )
        
        # Additional Tests: Test different symbols and timeframes
        print("Testing additional symbols and timeframes...")
        print()
        
        # Test with different symbols
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/chart-data/ETHUSDT/4h",
            validate_data=self.validate_chart_data,
            test_name="Chart Data API (ETHUSDT/4h)"
        )
        
        # Test with different timeframes
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/suggestions/BTCUSDT/15m",
            validate_data=self.validate_suggestions,
            test_name="Suggestions API (BTCUSDT/15m)"
        )
        
        # Test specific indicator endpoints
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/available-indicators",
            test_name="Available Indicators API"
        )
        
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/available-overlays",
            test_name="Available Overlays API"
        )

    def test_advanced_features(self):
        """Test advanced features and edge cases"""
        print("Testing advanced features and edge cases...")
        print()
        
        # Test Support/Resistance Detection
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/support-resistance/BTCUSDT/1h",
            test_name="Support/Resistance Detection"
        )
        
        # Test Liquidity Zones
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/liquidity-zones/BTCUSDT/1h",
            test_name="Liquidity Zones Detection"
        )
        
        # Test with different parameters
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/chart-data/BTCUSDT/1h?limit=100",
            validate_data=self.validate_chart_data,
            test_name="Chart Data with Custom Limit"
        )
        
        # Test fractal matches with different parameters
        self.test_endpoint(
            "GET", "/api/v1/research-analytics/fractal-matches/BTCUSDT/1h?min_similarity=0.8&limit=5",
            validate_data=self.validate_fractal_matches,
            test_name="Fractal Matches with Parameters"
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": self.tests_run,
                "passed_tests": self.tests_passed,
                "failed_tests": self.tests_run - self.tests_passed,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_environment": {
                "base_url": self.base_url,
                "phase": "47-48",
                "module": "research_analytics"
            }
        }
        
        # Save to file
        with open("/app/backend_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # List failed tests
        failed_tests = [r for r in self.results if not r["passed"]]
        if failed_tests:
            print("FAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test_name']}: {test['details']}")
        else:
            print("✅ All tests passed!")
        
        print()
        print("=" * 80)


def main():
    """Main test execution"""
    tester = ResearchAnalyticsAPITester()
    
    # Run all tests
    tester.run_all_tests()
    tester.test_advanced_features()
    
    # Generate and save report
    report = tester.generate_report()
    
    # Print summary
    tester.print_summary()
    
    # Return appropriate exit code
    return 0 if tester.tests_passed == tester.tests_run else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)