#!/usr/bin/env python3
"""
Backend Testing for PHASE 52: Frontend Readiness Audit
======================================================

Tests:
- PHASE 52: Frontend Readiness Audit Module
- Dashboard and System Status endpoints

Target Endpoints:
- GET /api/v1/frontend-readiness/health - PHASE 52 module health
- POST /api/v1/frontend-readiness/audit - run full audit (should return frontend_ready: true)
- GET /api/v1/frontend-readiness/audit/summary - quick summary
- GET /api/v1/frontend-readiness/standards - frontend standards documentation
- GET /api/v1/dashboard/overview - aggregated dashboard for terminal
- GET /api/v1/system/status/dashboard - system status for top-bar
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class Phase52_FrontendReadinessAPITester:
    def __init__(self, base_url: str = "https://ta-detector-preview.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test configuration
        self.timeout = 30  # seconds
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TA-Engine-Frontend-Readiness-Tester/1.0'
        }

    def log_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        if passed:
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            print(f"   Details: {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200) -> tuple[bool, Dict[str, Any]]:
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Check status code
            status_ok = response.status_code == expected_status
            
            # Try to parse JSON
            try:
                json_data = response.json()
            except ValueError:
                json_data = {"error": "Invalid JSON response", "text": response.text[:500]}

            details = {
                "url": url,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response_data": json_data
            }

            if status_ok:
                self.tests_passed += 1
                self.log_result(name, True, details)
                return True, json_data
            else:
                self.log_result(name, False, details)
                return False, json_data

        except requests.exceptions.Timeout:
            details = {
                "url": url,
                "error": "Request timeout",
                "timeout_seconds": self.timeout
            }
            self.log_result(name, False, details)
            return False, details

        except requests.exceptions.ConnectionError:
            details = {
                "url": url,
                "error": "Connection error - service may be down"
            }
            self.log_result(name, False, details)
            return False, details

        except Exception as e:
            details = {
                "url": url,
                "error": str(e)
            }
            self.log_result(name, False, details)
            return False, details

    def test_phase_52_frontend_readiness(self):
        """Test PHASE 52: Frontend Readiness Audit"""
        print("\n" + "="*60)
        print("TESTING PHASE 52: FRONTEND READINESS AUDIT")
        print("="*60)

        # Test health endpoint
        success, data = self.run_test(
            "Frontend Readiness Health Check",
            "GET",
            "/api/v1/frontend-readiness/health"
        )

        if success:
            # Validate response structure
            required_fields = ["status", "phase", "module"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in health response: {missing}")
            else:
                print(f"   📊 Phase: {data.get('phase', 'N/A')}")
                print(f"   📊 Module: {data.get('module', 'N/A')}")

        # Test full audit endpoint - this is the main test
        print("\n🔍 Running full frontend readiness audit (may take a moment)...")
        success, audit_data = self.run_test(
            "Frontend Readiness Full Audit",
            "POST",
            "/api/v1/frontend-readiness/audit"
        )

        if success:
            # Validate audit response structure
            required_audit_fields = [
                "report_id", "timestamp", "overall_score", 
                "frontend_ready", "passed", "warnings", "failed"
            ]
            missing = [f for f in required_audit_fields if f not in audit_data]
            if missing:
                print(f"   ⚠️  Missing fields in audit response: {missing}")
            else:
                overall_score = audit_data.get('overall_score', 0)
                frontend_ready = audit_data.get('frontend_ready', False)
                
                print(f"   📊 Report ID: {audit_data.get('report_id', 'N/A')}")
                print(f"   📊 Overall Score: {overall_score}/100")
                print(f"   📊 Frontend Ready: {frontend_ready}")
                print(f"   📊 Tests Passed: {audit_data.get('passed', 0)}")
                print(f"   📊 Warnings: {audit_data.get('warnings', 0)}")
                print(f"   📊 Failed: {audit_data.get('failed', 0)}")
                
                # Check if meets requirements (score >= 85 and frontend_ready = true)
                if frontend_ready and overall_score >= 85:
                    print("   ✅ FRONTEND READINESS REQUIREMENTS MET!")
                else:
                    print("   ❌ FRONTEND READINESS REQUIREMENTS NOT MET")
                    print(f"      Required: frontend_ready=True AND score>=85")
                    print(f"      Actual: frontend_ready={frontend_ready} AND score={overall_score}")
                
                # Show category scores
                score_fields = [
                    "api_consistency_score", "response_size_score", "pagination_score",
                    "standardization_score", "stability_score", "extensibility_score", "limits_score"
                ]
                
                print("   📈 Category Scores:")
                for field in score_fields:
                    if field in audit_data:
                        category = field.replace('_score', '').replace('_', ' ').title()
                        print(f"      {category}: {audit_data[field]}/100")
                
                # Show critical issues if any
                critical_issues = audit_data.get('critical_issues', [])
                if critical_issues:
                    print("   🚨 Critical Issues:")
                    for issue in critical_issues:
                        print(f"      - {issue}")
                
                # Show recommendations
                recommendations = audit_data.get('recommendations', [])
                if recommendations:
                    print("   💡 Recommendations:")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"      - {rec}")

        # Test audit summary endpoint
        success, summary_data = self.run_test(
            "Frontend Readiness Audit Summary",
            "GET",
            "/api/v1/frontend-readiness/audit/summary"
        )

        if success:
            expected_fields = ["frontend_ready", "overall_score", "scores", "passed", "warnings", "failed"]
            missing = [f for f in expected_fields if f not in summary_data]
            if missing:
                print(f"   ⚠️  Missing fields in summary response: {missing}")

        # Test standards endpoint
        success, standards_data = self.run_test(
            "Frontend Readiness Standards",
            "GET",
            "/api/v1/frontend-readiness/standards"
        )

        if success:
            # Validate standards response
            expected_sections = ["symbols", "timeframes", "chart_object", "limits", "performance"]
            missing = [f for f in expected_sections if f not in standards_data]
            if missing:
                print(f"   ⚠️  Missing sections in standards: {missing}")
            else:
                symbols = standards_data.get('symbols', {}).get('supported', [])
                timeframes = standards_data.get('timeframes', {}).get('supported', [])
                limits = standards_data.get('limits', {})
                
                print(f"   📊 Supported Symbols: {len(symbols)} symbols")
                print(f"   📊 Supported Timeframes: {len(timeframes)} timeframes")
                print(f"   📊 Object Limits: {len(limits.get('objects', {}))}")
                print(f"   📊 Max Response Size: {standards_data.get('performance', {}).get('max_response_size_kb', 'N/A')}KB")

    def test_dashboard_endpoints(self):
        """Test Dashboard and System Status endpoints"""
        print("\n" + "="*60)
        print("TESTING DASHBOARD & SYSTEM STATUS")
        print("="*60)

        # Test dashboard overview endpoint
        success, data = self.run_test(
            "Dashboard Overview",
            "GET",
            "/api/v1/dashboard/overview"
        )

        if success:
            # This endpoint might not exist, so just log what we get
            print(f"   📊 Dashboard Overview Response Keys: {list(data.keys())}")

        # Test system status dashboard
        success, data = self.run_test(
            "System Status Dashboard",
            "GET",
            "/api/v1/system/status/dashboard"
        )

        if success:
            # Validate dashboard response
            expected_sections = ["system", "execution", "portfolio", "risk", "pnl", "market"]
            missing = [f for f in expected_sections if f not in data]
            if missing:
                print(f"   ⚠️  Missing sections in dashboard: {missing}")
            else:
                system = data.get('system', {})
                print(f"   💻 System Health: {system.get('health', 'N/A')}")
                print(f"   💻 System Mode: {system.get('mode', 'N/A')}")
                print(f"   💻 Version: {system.get('version', 'N/A')}")
                
                market = data.get('market', {})
                print(f"   📈 Market Regime: {market.get('regime', 'N/A')}")
                print(f"   💰 Capital Flow: {market.get('capital_flow_bias', 'N/A')}")

    def run_all_tests(self):
        """Run all test suites"""
        start_time = time.time()
        
        print("🚀 Starting PHASE 52 Frontend Readiness Backend API Testing")
        print(f"Target: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all test phases
        self.test_phase_52_frontend_readiness()
        self.test_dashboard_endpoints()
        
        # Final summary
        elapsed = time.time() - start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "="*60)
        print("FINAL TEST SUMMARY")
        print("="*60)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {elapsed:.2f} seconds")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if not r["passed"] and "health" in r["test_name"].lower()]
        if critical_failures:
            print(f"\n🚨 CRITICAL: {len(critical_failures)} health check failures!")
            for failure in critical_failures:
                print(f"   - {failure['test_name']}")
        
        return self.tests_passed == self.tests_run

    def get_test_summary(self):
        """Get detailed test summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "test_results": self.test_results,
            "phases_tested": [
                "PHASE 52: Frontend Readiness Audit",
                "Dashboard and System Status Endpoints"
            ]
        }


def main():
    """Main test runner"""
    tester = Phase52_FrontendReadinessAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save test results
        summary = tester.get_test_summary()
        
        with open("/app/test_results_phase_52.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Test results saved to: /app/test_results_phase_52.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())