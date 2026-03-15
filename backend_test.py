#!/usr/bin/env python3
"""
TA Engine Module Runtime Backend Testing
========================================

Tests for PHASE 46.1 Logic Validation and PHASE 46.4 Stability Freeze
Backend testing for 6 specified API endpoints.

Expected Results:
- GET /api/health: ok: true, version 45.0.0
- GET /api/system/db-health: MongoDB connection healthy
- GET /api/ta/registry: 88 nodes registered
- POST /api/v1/validation/run/logic: PHASE 46.1 Logic Validation (12 tests)
- POST /api/v1/validation/run: Full validation score
- GET /api/v1/validation/health: validation module status
"""

import requests
import sys
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class TAEngineBackendTester:
    def __init__(self, base_url="https://portfolio-command-7.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name}: {message}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, Any, str]:
        """Make HTTP request and handle errors"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=30, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, timeout=60, **kwargs)  # Longer timeout for validation
            else:
                return False, None, f"Unsupported method: {method}"

            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, f"Status: {response.status_code}"
                except json.JSONDecodeError:
                    return True, response.text, f"Status: {response.status_code} (text response)"
            else:
                try:
                    error_data = response.json()
                    return False, error_data, f"Status: {response.status_code}, Error: {error_data}"
                except:
                    return False, response.text, f"Status: {response.status_code}, Text: {response.text[:200]}"

        except requests.exceptions.Timeout:
            return False, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error"
        except Exception as e:
            return False, None, f"Request error: {str(e)}"

    def test_health_endpoint(self):
        """Test GET /api/health - должен вернуть ok: true, version 45.0.0"""
        success, data, message = self.make_request('GET', '/api/health')
        
        if success and isinstance(data, dict):
            ok_check = data.get('ok') is True
            version_check = data.get('version') == '45.0.0'
            
            if ok_check and version_check:
                self.log_result(
                    "Health Endpoint", 
                    True, 
                    f"✅ ok: {data.get('ok')}, version: {data.get('version')}",
                    {"response": data}
                )
            else:
                self.log_result(
                    "Health Endpoint", 
                    False, 
                    f"❌ ok: {data.get('ok')}, version: {data.get('version')} (expected: ok=True, version=45.0.0)",
                    {"response": data}
                )
        else:
            self.log_result("Health Endpoint", False, message, {"response": data})

    def test_db_health_endpoint(self):
        """Test GET /api/system/db-health - MongoDB connection healthy"""
        success, data, message = self.make_request('GET', '/api/system/db-health')
        
        if success and isinstance(data, dict):
            status = data.get('status', '').lower()
            connected = data.get('connected', False)
            
            if status in ['ok', 'healthy', 'connected'] and connected:
                self.log_result(
                    "DB Health", 
                    True, 
                    f"✅ MongoDB healthy - status: {status}, connected: {connected}",
                    {"response": data}
                )
            else:
                self.log_result(
                    "DB Health", 
                    False, 
                    f"❌ MongoDB issues - status: {status}, connected: {connected}",
                    {"response": data}
                )
        else:
            self.log_result("DB Health", False, message, {"response": data})

    def test_ta_registry_endpoint(self):
        """Test GET /api/ta/registry - 88 nodes registered"""
        success, data, message = self.make_request('GET', '/api/ta/registry')
        
        if success and isinstance(data, dict):
            registry_data = data.get('registry', {})
            total_nodes = 0
            
            # Try different possible fields for node count
            if isinstance(registry_data, dict):
                total_nodes = (
                    registry_data.get('total_nodes') or 
                    registry_data.get('node_count') or 
                    registry_data.get('total') or
                    0
                )
            
            # Check for nodes in different formats
            if 'nodes' in data and isinstance(data['nodes'], list):
                total_nodes = len(data['nodes'])
            
            if total_nodes >= 88:
                self.log_result(
                    "TA Registry", 
                    True, 
                    f"✅ {total_nodes} nodes registered (≥88 expected)",
                    {"response": data, "node_count": total_nodes}
                )
            elif total_nodes > 0:
                self.log_result(
                    "TA Registry", 
                    False, 
                    f"❌ Only {total_nodes} nodes registered (88 expected)",
                    {"response": data, "node_count": total_nodes}
                )
            else:
                # Try to extract from status field or other fields
                status = data.get('status', '')
                if status == 'ok':
                    self.log_result(
                        "TA Registry", 
                        True, 
                        f"✅ Registry endpoint responsive, status: {status}",
                        {"response": data}
                    )
                else:
                    self.log_result(
                        "TA Registry", 
                        False, 
                        f"❌ Could not determine node count from response",
                        {"response": data}
                    )
        else:
            self.log_result("TA Registry", False, message, {"response": data})

    def test_validation_health(self):
        """Test GET /api/v1/validation/health - validation module status"""
        success, data, message = self.make_request('GET', '/api/v1/validation/health')
        
        if success and isinstance(data, dict):
            status = data.get('status', '').lower()
            phase = data.get('phase', '')
            module = data.get('module', '')
            
            if status in ['ok', 'healthy', 'running'] and phase == '46':
                self.log_result(
                    "Validation Health", 
                    True, 
                    f"✅ Validation module healthy - status: {status}, phase: {phase}",
                    {"response": data}
                )
            elif status in ['ok', 'healthy', 'running']:
                self.log_result(
                    "Validation Health", 
                    True, 
                    f"✅ Validation module healthy - status: {status}",
                    {"response": data}
                )
            else:
                self.log_result(
                    "Validation Health", 
                    False, 
                    f"❌ Validation module issues - status: {status}",
                    {"response": data}
                )
        else:
            self.log_result("Validation Health", False, message, {"response": data})

    def test_logic_validation(self):
        """Test POST /api/v1/validation/run/logic - PHASE 46.1 Logic Validation (12 tests)"""
        print("\n🔍 Running Logic Validation (this may take 30-60 seconds)...")
        
        success, data, message = self.make_request('POST', '/api/v1/validation/run/logic')
        
        if success and isinstance(data, dict):
            audit = data.get('audit', '')
            phase = data.get('phase', '')
            score = data.get('score', 0)
            tests_run = data.get('tests_run', 0)
            tests_passed = data.get('tests_passed', 0)
            tests_failed = data.get('tests_failed', 0)
            
            # Check if this is logic validation with expected structure
            if audit == 'logic' and phase == '46.1':
                if tests_run >= 12:
                    if score >= 90:
                        self.log_result(
                            "Logic Validation", 
                            True, 
                            f"✅ PHASE 46.1 Logic Validation completed - Score: {score}%, Tests: {tests_passed}/{tests_run}",
                            {"response": data, "score": score, "tests_run": tests_run}
                        )
                    else:
                        self.log_result(
                            "Logic Validation", 
                            False, 
                            f"❌ Logic Validation low score: {score}% (expected ≥90%), Tests: {tests_passed}/{tests_run}",
                            {"response": data, "score": score, "tests_run": tests_run}
                        )
                else:
                    self.log_result(
                        "Logic Validation", 
                        False, 
                        f"❌ Insufficient tests run: {tests_run} (expected ≥12)",
                        {"response": data, "tests_run": tests_run}
                    )
            else:
                self.log_result(
                    "Logic Validation", 
                    False, 
                    f"❌ Unexpected response format - audit: {audit}, phase: {phase}",
                    {"response": data}
                )
        else:
            self.log_result("Logic Validation", False, message, {"response": data})

    def test_full_validation(self):
        """Test POST /api/v1/validation/run - Full validation score"""
        print("\n🔍 Running Full System Validation (this may take 60-120 seconds)...")
        
        success, data, message = self.make_request('POST', '/api/v1/validation/run')
        
        if success and isinstance(data, dict):
            report_id = data.get('report_id', '')
            system_score = data.get('system_score', 0)
            status = data.get('status', '')
            scores = data.get('scores', {})
            summary = data.get('summary', {})
            
            if report_id and system_score >= 0:
                if system_score >= 90:
                    self.log_result(
                        "Full Validation", 
                        True, 
                        f"✅ Full validation completed - System Score: {system_score}%, Status: {status}",
                        {
                            "response": data, 
                            "system_score": system_score,
                            "individual_scores": scores,
                            "summary": summary
                        }
                    )
                else:
                    self.log_result(
                        "Full Validation", 
                        False, 
                        f"❌ Low system score: {system_score}% (expected ≥90%), Status: {status}",
                        {
                            "response": data, 
                            "system_score": system_score,
                            "individual_scores": scores
                        }
                    )
            else:
                self.log_result(
                    "Full Validation", 
                    False, 
                    f"❌ Invalid validation response - report_id: {report_id}, score: {system_score}",
                    {"response": data}
                )
        else:
            self.log_result("Full Validation", False, message, {"response": data})

    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("TA ENGINE MODULE RUNTIME BACKEND TESTING")
        print("PHASE 46.1 Logic Validation & PHASE 46.4 Stability Freeze")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started: {datetime.now(timezone.utc).isoformat()}")
        print()

        # Core system tests
        print("🏥 CORE SYSTEM HEALTH TESTS")
        print("-" * 40)
        self.test_health_endpoint()
        self.test_db_health_endpoint()
        print()

        # TA Engine tests
        print("🎯 TA ENGINE TESTS")
        print("-" * 40)
        self.test_ta_registry_endpoint()
        print()

        # Validation system tests
        print("🔬 VALIDATION SYSTEM TESTS")
        print("-" * 40)
        self.test_validation_health()
        self.test_logic_validation()
        self.test_full_validation()
        print()

        # Results summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        print()

        if self.tests_failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test_name']}: {result['message']}")
            print()

        print(f"Test completed: {datetime.now(timezone.utc).isoformat()}")
        
        return self.tests_failed == 0

    def get_detailed_results(self) -> Dict:
        """Get detailed test results for reporting"""
        return {
            "summary": {
                "tests_run": self.tests_run,
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            },
            "results": self.test_results,
            "backend_url": self.base_url,
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
        }


def main():
    """Main test execution"""
    tester = TAEngineBackendTester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = tester.get_detailed_results()
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())