#!/usr/bin/env python3
"""
MCPO Health Check Script

Comprehensive health monitoring for MCPO and related services.
Can be used for monitoring, alerting, and automated health checks.
"""

import requests
import json
import time
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import socket
from urllib.parse import urlparse

class HealthChecker:
    """Comprehensive health checker for MCPO system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'unknown',
            'checks': {},
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        
        checks = [
            ('mcpo_connectivity', self._check_mcpo_connectivity),
            ('mcpo_authentication', self._check_mcpo_authentication),
            ('mcpo_tools', self._check_mcpo_tools),
            ('mcpo_performance', self._check_mcpo_performance),
            ('system_resources', self._check_system_resources),
            ('docker_health', self._check_docker_health),
            ('database_health', self._check_database_health),
            ('network_connectivity', self._check_network_connectivity),
        ]
        
        for check_name, check_func in checks:
            if self._should_run_check(check_name):
                self.results['checks'][check_name] = self._run_check(check_func)
        
        self._calculate_summary()
        return self.results
    
    def _should_run_check(self, check_name: str) -> bool:
        """Determine if a check should be run based on configuration"""
        enabled_checks = self.config.get('enabled_checks', [])
        if enabled_checks:
            return check_name in enabled_checks
        
        disabled_checks = self.config.get('disabled_checks', [])
        return check_name not in disabled_checks
    
    def _run_check(self, check_func) -> Dict[str, Any]:
        """Run a single check with error handling"""
        start_time = time.time()
        
        try:
            result = check_func()
            result['duration'] = round(time.time() - start_time, 3)
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Check failed with exception: {e}",
                'duration': round(time.time() - start_time, 3),
                'details': {}
            }
    
    def _check_mcpo_connectivity(self) -> Dict[str, Any]:
        """Check MCPO basic connectivity"""
        mcpo_url = self.config.get('mcpo_url', 'http://localhost:8000')
        timeout = self.config.get('timeout', 10)
        
        try:
            response = requests.get(
                f"{mcpo_url}/docs",
                timeout=timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return {
                    'status': 'pass',
                    'message': 'MCPO is responding',
                    'details': {
                        'url': mcpo_url,
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                }
            else:
                return {
                    'status': 'fail',
                    'message': f'MCPO returned HTTP {response.status_code}',
                    'details': {
                        'url': mcpo_url,
                        'status_code': response.status_code
                    }
                }
        
        except requests.exceptions.ConnectTimeout:
            return {
                'status': 'fail',
                'message': 'Connection timeout',
                'details': {'url': mcpo_url, 'timeout': timeout}
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'fail',
                'message': 'Connection refused',
                'details': {'url': mcpo_url}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Unexpected error: {e}',
                'details': {'url': mcpo_url}
            }
    
    def _check_mcpo_authentication(self) -> Dict[str, Any]:
        """Check MCPO authentication"""
        mcpo_url = self.config.get('mcpo_url', 'http://localhost:8000')
        api_key = self.config.get('api_key')
        timeout = self.config.get('timeout', 10)
        
        if not api_key:
            return {
                'status': 'skip',
                'message': 'No API key configured',
                'details': {}
            }
        
        try:
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(
                f"{mcpo_url}/docs",
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return {
                    'status': 'pass',
                    'message': 'Authentication successful',
                    'details': {
                        'status_code': response.status_code,
                        'api_key_length': len(api_key)
                    }
                }
            elif response.status_code in (401, 403):
                return {
                    'status': 'fail',
                    'message': f'Authentication failed (HTTP {response.status_code})',
                    'details': {'status_code': response.status_code}
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'Unexpected status code: {response.status_code}',
                    'details': {'status_code': response.status_code}
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Authentication check failed: {e}',
                'details': {}
            }
    
    def _check_mcpo_tools(self) -> Dict[str, Any]:
        """Check individual MCPO tools"""
        mcpo_url = self.config.get('mcpo_url', 'http://localhost:8000')
        api_key = self.config.get('api_key')
        timeout = self.config.get('timeout', 10)
        tools = self.config.get('tools', [])
        
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        tool_results = {}
        overall_status = 'pass'
        
        try:
            # Try to discover tools from OpenAPI spec
            if not tools:
                try:
                    response = requests.get(
                        f"{mcpo_url}/openapi.json",
                        headers=headers,
                        timeout=timeout
                    )
                    if response.status_code == 200:
                        spec = response.json()
                        paths = spec.get('paths', {})
                        tools = [path.strip('/') for path in paths.keys() 
                                if path not in ('/', '/docs', '/openapi.json') and path.startswith('/')]
                except:
                    pass
            
            # If no tools discovered, test base endpoint
            if not tools:
                tools = ['']  # Empty string for base endpoint
            
            for tool in tools:
                tool_url = f"{mcpo_url}/{tool}".rstrip('/')
                try:
                    response = requests.get(tool_url, headers=headers, timeout=timeout)
                    
                    if response.status_code == 200:
                        tool_results[tool or 'base'] = {
                            'status': 'pass',
                            'status_code': response.status_code,
                            'response_time': response.elapsed.total_seconds()
                        }
                    else:
                        tool_results[tool or 'base'] = {
                            'status': 'fail',
                            'status_code': response.status_code
                        }
                        overall_status = 'fail'
                
                except Exception as e:
                    tool_results[tool or 'base'] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    overall_status = 'fail'
            
            return {
                'status': overall_status,
                'message': f'Checked {len(tool_results)} tools',
                'details': {
                    'tools': tool_results,
                    'total_tools': len(tool_results),
                    'working_tools': sum(1 for r in tool_results.values() if r['status'] == 'pass')
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Tool check failed: {e}',
                'details': {}
            }
    
    def _check_mcpo_performance(self) -> Dict[str, Any]:
        """Check MCPO performance metrics"""
        mcpo_url = self.config.get('mcpo_url', 'http://localhost:8000')
        api_key = self.config.get('api_key')
        timeout = self.config.get('timeout', 10)
        performance_threshold = self.config.get('performance_threshold', 2.0)  # seconds
        
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            # Run multiple requests to get average response time
            response_times = []
            for _ in range(3):
                start = time.time()
                response = requests.get(f"{mcpo_url}/docs", headers=headers, timeout=timeout)
                response_times.append(time.time() - start)
                
                if response.status_code != 200:
                    return {
                        'status': 'fail',
                        'message': f'Performance test failed with HTTP {response.status_code}',
                        'details': {'status_code': response.status_code}
                    }
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time > performance_threshold:
                status = 'warning'
                message = f'Average response time ({avg_response_time:.3f}s) exceeds threshold ({performance_threshold}s)'
            else:
                status = 'pass'
                message = f'Performance acceptable (avg: {avg_response_time:.3f}s)'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'avg_response_time': round(avg_response_time, 3),
                    'max_response_time': round(max_response_time, 3),
                    'min_response_time': round(min(response_times), 3),
                    'threshold': performance_threshold,
                    'samples': len(response_times)
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Performance check failed: {e}',
                'details': {}
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Load average (Unix-like systems)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except:
                pass
            
            # Determine status based on thresholds
            cpu_threshold = self.config.get('cpu_threshold', 80)
            memory_threshold = self.config.get('memory_threshold', 80)
            disk_threshold = self.config.get('disk_threshold', 90)
            
            status = 'pass'
            issues = []
            
            if cpu_percent > cpu_threshold:
                status = 'warning'
                issues.append(f'High CPU usage: {cpu_percent}%')
            
            if memory_percent > memory_threshold:
                status = 'warning'
                issues.append(f'High memory usage: {memory_percent}%')
            
            if disk_percent > disk_threshold:
                status = 'fail'
                issues.append(f'High disk usage: {disk_percent}%')
            
            return {
                'status': status,
                'message': '; '.join(issues) if issues else 'System resources normal',
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': disk_percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'load_average': load_avg
                }
            }
        
        except ImportError:
            return {
                'status': 'skip',
                'message': 'psutil not available for system resource monitoring',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'System resource check failed: {e}',
                'details': {}
            }
    
    def _check_docker_health(self) -> Dict[str, Any]:
        """Check Docker container health"""
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return {
                    'status': 'skip',
                    'message': 'Docker not available',
                    'details': {}
                }
            
            # Get container information
            containers = self.config.get('docker_containers', ['mcpo', 'open-webui'])
            container_info = {}
            
            for container_name in containers:
                try:
                    # Get container status
                    inspect_result = subprocess.run(
                        ['docker', 'inspect', container_name, '--format', '{{.State.Status}}'],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if inspect_result.returncode == 0:
                        status = inspect_result.stdout.strip()
                        container_info[container_name] = {'status': status}
                        
                        # Get health check status if available
                        health_result = subprocess.run(
                            ['docker', 'inspect', container_name, '--format', '{{.State.Health.Status}}'],
                            capture_output=True, text=True, timeout=5
                        )
                        
                        if health_result.returncode == 0:
                            health_status = health_result.stdout.strip()
                            if health_status != '<no value>':
                                container_info[container_name]['health'] = health_status
                    else:
                        container_info[container_name] = {'status': 'not found'}
                
                except Exception as e:
                    container_info[container_name] = {'error': str(e)}
            
            # Determine overall status
            running_containers = sum(1 for info in container_info.values() 
                                   if info.get('status') == 'running')
            total_containers = len(container_info)
            
            if running_containers == total_containers:
                status = 'pass'
                message = f'All {total_containers} containers running'
            elif running_containers > 0:
                status = 'warning'
                message = f'{running_containers}/{total_containers} containers running'
            else:
                status = 'fail'
                message = 'No containers running'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'containers': container_info,
                    'running': running_containers,
                    'total': total_containers
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Docker health check failed: {e}',
                'details': {}
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        db_config = self.config.get('database', {})
        if not db_config:
            return {
                'status': 'skip',
                'message': 'No database configuration',
                'details': {}
            }
        
        db_type = db_config.get('type', 'postgresql')
        
        if db_type == 'postgresql':
            return self._check_postgresql_health(db_config)
        elif db_type == 'redis':
            return self._check_redis_health(db_config)
        else:
            return {
                'status': 'skip',
                'message': f'Unknown database type: {db_type}',
                'details': {}
            }
    
    def _check_postgresql_health(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check PostgreSQL health"""
        try:
            import psycopg2
            
            host = config.get('host', 'localhost')
            port = config.get('port', 5432)
            database = config.get('database', 'openwebui')
            user = config.get('user', 'postgres')
            password = config.get('password', '')
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            
            cursor.execute('SELECT pg_database_size(current_database());')
            db_size = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'pass',
                'message': 'PostgreSQL connection successful',
                'details': {
                    'host': host,
                    'port': port,
                    'database': database,
                    'version': version,
                    'size_mb': round(db_size / (1024*1024), 2)
                }
            }
        
        except ImportError:
            return {
                'status': 'skip',
                'message': 'psycopg2 not available',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'PostgreSQL connection failed: {e}',
                'details': {'host': config.get('host'), 'port': config.get('port')}
            }
    
    def _check_redis_health(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            import redis
            
            host = config.get('host', 'localhost')
            port = config.get('port', 6379)
            password = config.get('password')
            
            r = redis.Redis(
                host=host,
                port=port,
                password=password,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            info = r.info()
            
            return {
                'status': 'pass',
                'message': 'Redis connection successful',
                'details': {
                    'host': host,
                    'port': port,
                    'version': info.get('redis_version'),
                    'used_memory_mb': round(info.get('used_memory', 0) / (1024*1024), 2),
                    'connected_clients': info.get('connected_clients')
                }
            }
        
        except ImportError:
            return {
                'status': 'skip',
                'message': 'redis package not available',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Redis connection failed: {e}',
                'details': {'host': config.get('host'), 'port': config.get('port')}
            }
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to external services"""
        external_services = self.config.get('external_services', [])
        if not external_services:
            return {
                'status': 'skip',
                'message': 'No external services configured',
                'details': {}
            }
        
        results = {}
        overall_status = 'pass'
        
        for service in external_services:
            service_name = service.get('name', 'unknown')
            url = service.get('url')
            
            if not url:
                results[service_name] = {'status': 'error', 'message': 'No URL configured'}
                continue
            
            try:
                parsed_url = urlparse(url)
                host = parsed_url.hostname
                port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
                
                # Test TCP connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    results[service_name] = {'status': 'pass', 'host': host, 'port': port}
                else:
                    results[service_name] = {'status': 'fail', 'host': host, 'port': port}
                    overall_status = 'fail'
            
            except Exception as e:
                results[service_name] = {'status': 'error', 'error': str(e)}
                overall_status = 'fail'
        
        working_services = sum(1 for r in results.values() if r['status'] == 'pass')
        total_services = len(results)
        
        return {
            'status': overall_status,
            'message': f'{working_services}/{total_services} external services reachable',
            'details': {
                'services': results,
                'working': working_services,
                'total': total_services
            }
        }
    
    def _calculate_summary(self):
        """Calculate overall summary"""
        total = len(self.results['checks'])
        passed = sum(1 for check in self.results['checks'].values() 
                    if check['status'] == 'pass')
        failed = sum(1 for check in self.results['checks'].values() 
                    if check['status'] == 'fail')
        warnings = sum(1 for check in self.results['checks'].values() 
                      if check['status'] == 'warning')
        
        self.results['summary'] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'skipped': total - passed - failed - warnings
        }
        
        if failed > 0:
            self.results['overall_status'] = 'fail'
        elif warnings > 0:
            self.results['overall_status'] = 'warning'
        else:
            self.results['overall_status'] = 'pass'


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config = {
        'mcpo_url': os.getenv('MCPO_URL', 'http://localhost:8000'),
        'api_key': os.getenv('API_KEY'),
        'timeout': int(os.getenv('HEALTH_CHECK_TIMEOUT', '10')),
        'performance_threshold': float(os.getenv('PERFORMANCE_THRESHOLD', '2.0')),
        'cpu_threshold': int(os.getenv('CPU_THRESHOLD', '80')),
        'memory_threshold': int(os.getenv('MEMORY_THRESHOLD', '80')),
        'disk_threshold': int(os.getenv('DISK_THRESHOLD', '90'))
    }
    
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    return config


def format_output(results: Dict[str, Any], format_type: str = 'human') -> str:
    """Format results for output"""
    if format_type == 'json':
        return json.dumps(results, indent=2)
    
    elif format_type == 'human':
        output = []
        output.append(f"🏥 MCPO Health Check Report")
        output.append(f"📅 Timestamp: {results['timestamp']}")
        output.append(f"📊 Overall Status: {results['overall_status'].upper()}")
        output.append("")
        
        summary = results['summary']
        output.append(f"📈 Summary:")
        output.append(f"   Total Checks: {summary['total']}")
        output.append(f"   ✅ Passed: {summary['passed']}")
        output.append(f"   ❌ Failed: {summary['failed']}")
        output.append(f"   ⚠️  Warnings: {summary['warnings']}")
        output.append(f"   ⏭️  Skipped: {summary['skipped']}")
        output.append("")
        
        for check_name, check_result in results['checks'].items():
            status_emoji = {
                'pass': '✅',
                'fail': '❌',
                'warning': '⚠️',
                'error': '💥',
                'skip': '⏭️'
            }.get(check_result['status'], '❓')
            
            output.append(f"{status_emoji} {check_name.replace('_', ' ').title()}")
            output.append(f"   Status: {check_result['status']}")
            output.append(f"   Message: {check_result['message']}")
            output.append(f"   Duration: {check_result.get('duration', 0)}s")
            
            if check_result.get('details'):
                output.append(f"   Details: {json.dumps(check_result['details'], indent=4)}")
            output.append("")
        
        return "\n".join(output)
    
    elif format_type == 'prometheus':
        # Prometheus metrics format
        metrics = []
        timestamp = int(time.time() * 1000)
        
        # Overall status
        status_value = {'pass': 1, 'warning': 0.5, 'fail': 0}.get(results['overall_status'], 0)
        metrics.append(f'mcpo_health_overall{{}} {status_value} {timestamp}')
        
        # Individual checks
        for check_name, check_result in results['checks'].items():
            check_value = {'pass': 1, 'warning': 0.5, 'fail': 0, 'error': 0, 'skip': -1}.get(check_result['status'], 0)
            metrics.append(f'mcpo_health_check{{check="{check_name}"}} {check_value} {timestamp}')
            
            # Duration
            duration = check_result.get('duration', 0)
            metrics.append(f'mcpo_health_check_duration{{check="{check_name}"}} {duration} {timestamp}')
        
        return "\n".join(metrics)
    
    else:
        raise ValueError(f"Unknown format type: {format_type}")


def main():
    parser = argparse.ArgumentParser(description="MCPO Health Check")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--format', choices=['human', 'json', 'prometheus'], 
                       default='human', help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--exit-code', action='store_true', 
                       help='Exit with non-zero code on failures')
    parser.add_argument('--continuous', type=int, metavar='SECONDS',
                       help='Run continuously with specified interval')
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    def run_health_check():
        checker = HealthChecker(config)
        results = checker.run_all_checks()
        
        output = format_output(results, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
        
        if args.exit_code and results['overall_status'] == 'fail':
            return 1
        return 0
    
    if args.continuous:
        try:
            while True:
                exit_code = run_health_check()
                if args.format == 'human':
                    print(f"\n{'='*50}")
                    print(f"Next check in {args.continuous} seconds...")
                    print(f"{'='*50}\n")
                time.sleep(args.continuous)
        except KeyboardInterrupt:
            print("\nHealth check monitoring stopped.")
            return 0
    else:
        return run_health_check()


if __name__ == '__main__':
    sys.exit(main())