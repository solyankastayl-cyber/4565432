#!/usr/bin/env python3
"""
Backend Testing for PHASES 49-51: Visual Objects, Chart Composer, Signal Explanation
===================================================================================

Tests:
- PHASE 49: Visual Objects Engine
- PHASE 50: Chart Composition Engine  
- PHASE 51: Signal Explanation Engine
- System Dashboard Status

Target Endpoints:
- GET /api/v1/visual-objects/health
- GET /api/v1/visual-objects/types
- GET /api/v1/chart/health
- GET /api/v1/chart/presets
- GET /api/v1/chart/full-analysis/BTCUSDT/1h
- GET /api/v1/signal/health
- GET /api/v1/signal/explanation/BTCUSDT/1h
- GET /api/v1/signal/drivers/BTCUSDT/1h
- GET /api/v1/system/status/dashboard
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class Phase49_51_APITester:
    def __init__(self, base_url: str = "https://ta-detector-preview.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test configuration
        self.timeout = 30  # seconds
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TA-Engine-Backend-Tester/1.0'
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

    def test_phase_49_visual_objects(self):
        """Test PHASE 49: Visual Objects Engine"""
        print("\n" + "="*60)
        print("TESTING PHASE 49: VISUAL OBJECTS ENGINE")
        print("="*60)

        # Test health endpoint
        success, data = self.run_test(
            "Visual Objects Health Check",
            "GET",
            "/api/v1/visual-objects/health"
        )

        if success:
            # Validate response structure
            required_fields = ["status", "phase", "module"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in health response: {missing}")

        # Test object types endpoint
        success, data = self.run_test(
            "Visual Objects Types",
            "GET",
            "/api/v1/visual-objects/types"
        )

        if success:
            # Validate object types structure
            expected_fields = ["types", "categories", "count"]
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in types response: {missing}")
            else:
                print(f"   📊 Found {data.get('count', 0)} object types")
                print(f"   📊 Categories: {', '.join(data.get('categories', []))}")

    def test_phase_50_chart_composer(self):
        """Test PHASE 50: Chart Composition Engine"""
        print("\n" + "="*60)
        print("TESTING PHASE 50: CHART COMPOSITION ENGINE")
        print("="*60)

        # Test health endpoint
        success, data = self.run_test(
            "Chart Composer Health Check",
            "GET",
            "/api/v1/chart/health"
        )

        if success:
            required_fields = ["status", "phase", "module"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in health response: {missing}")

        # Test presets endpoint
        success, data = self.run_test(
            "Chart Composer Presets",
            "GET",
            "/api/v1/chart/presets"
        )

        if success:
            if "presets" in data and data["presets"]:
                print(f"   📊 Found {len(data['presets'])} chart presets")
                for preset in data["presets"][:3]:  # Show first 3
                    print(f"   📋 Preset: {preset.get('name', 'Unknown')} ({preset.get('preset_id', 'Unknown')})")

        # Test main chart analysis endpoint
        print("\n🔍 Testing main chart analysis endpoint (may take longer)...")
        success, data = self.run_test(
            "Chart Full Analysis BTCUSDT/1h",
            "GET",
            "/api/v1/chart/full-analysis/BTCUSDT/1h"
        )

        if success:
            # Validate main chart response
            expected_fields = ["symbol", "timeframe", "market_regime", "candles", "objects"]
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in chart analysis: {missing}")
            else:
                print(f"   📊 Symbol: {data.get('symbol', 'N/A')}")
                print(f"   📊 Timeframe: {data.get('timeframe', 'N/A')}")
                print(f"   📊 Market Regime: {data.get('market_regime', 'N/A')}")
                print(f"   📊 Candles: {len(data.get('candles', []))}")
                print(f"   📊 Objects: {len(data.get('objects', []))}")
                
                # Check statistics
                stats = data.get('stats', {})
                if stats:
                    print(f"   📈 Stats: {stats}")

    def test_phase_51_signal_explanation(self):
        """Test PHASE 51: Signal Explanation Engine"""
        print("\n" + "="*60)
        print("TESTING PHASE 51: SIGNAL EXPLANATION ENGINE")
        print("="*60)

        # Test health endpoint
        success, data = self.run_test(
            "Signal Explanation Health Check",
            "GET",
            "/api/v1/signal/health"
        )

        # Test signal explanation endpoint
        print("\n🔍 Testing signal explanation (may take longer)...")
        success, data = self.run_test(
            "Signal Explanation BTCUSDT/1h",
            "GET",
            "/api/v1/signal/explanation/BTCUSDT/1h"
        )

        if success:
            # Validate explanation response
            expected_fields = ["signal_id", "direction", "confidence", "drivers", "summary"]
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in explanation: {missing}")
            else:
                print(f"   🎯 Signal Direction: {data.get('direction', 'N/A')}")
                print(f"   🎯 Confidence: {data.get('confidence', 0):.1%}")
                print(f"   🎯 Strength: {data.get('strength', 'N/A')}")
                print(f"   🎯 Drivers: {len(data.get('drivers', []))}")
                print(f"   📝 Summary: {data.get('summary', 'N/A')[:100]}...")

                # Show top drivers
                drivers = data.get('drivers', [])
                if drivers:
                    print("   🔧 Top Drivers:")
                    for driver in drivers[:3]:
                        print(f"     - {driver.get('name', 'Unknown')}: {driver.get('contribution', 0):.3f}")

        # Test simplified drivers endpoint
        success, data = self.run_test(
            "Signal Drivers BTCUSDT/1h",
            "GET",
            "/api/v1/signal/drivers/BTCUSDT/1h"
        )

        if success:
            expected_fields = ["direction", "confidence", "drivers", "summary"]
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print(f"   ⚠️  Missing fields in drivers response: {missing}")

    def test_system_dashboard_status(self):
        """Test System Dashboard Status"""
        print("\n" + "="*60)
        print("TESTING SYSTEM DASHBOARD STATUS")
        print("="*60)

        success, data = self.run_test(
            "System Dashboard Status",
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
        
        print("🚀 Starting PHASES 49-51 Backend API Testing")
        print(f"Target: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all test phases
        self.test_phase_49_visual_objects()
        self.test_phase_50_chart_composer()
        self.test_phase_51_signal_explanation()
        self.test_system_dashboard_status()
        
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
                "PHASE 49: Visual Objects Engine",
                "PHASE 50: Chart Composition Engine", 
                "PHASE 51: Signal Explanation Engine",
                "System Dashboard Status"
            ]
        }


def main():
    """Main test runner"""
    tester = Phase49_51_APITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save test results
        summary = tester.get_test_summary()
        
        with open("/app/test_results_phases_49_51.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Test results saved to: /app/test_results_phases_49_51.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())