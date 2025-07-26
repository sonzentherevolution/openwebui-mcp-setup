#!/usr/bin/env python3
"""
MCPO Configuration Validator

This script validates MCPO configuration files for syntax, structure,
and common issues that could prevent successful server startup.
"""

import json
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil
import re

class ConfigValidator:
    """Validates MCPO configuration files"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate_file(self, config_path: str) -> bool:
        """Validate a configuration file"""
        try:
            # Check file existence and readability
            if not os.path.exists(config_path):
                self.errors.append(f"Configuration file not found: {config_path}")
                return False
                
            if not os.access(config_path, os.R_OK):
                self.errors.append(f"Configuration file is not readable: {config_path}")
                return False
            
            # Load and parse JSON
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON syntax: {e}")
                    return False
            
            # Validate structure
            self._validate_structure(config)
            
            # Validate servers
            if 'mcpServers' in config:
                self._validate_servers(config['mcpServers'])
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Unexpected error validating config: {e}")
            return False
    
    def _validate_structure(self, config: Dict[str, Any]):
        """Validate overall configuration structure"""
        
        # Check required top-level keys
        if 'mcpServers' not in config:
            self.errors.append("Missing required 'mcpServers' key")
            return
        
        if not isinstance(config['mcpServers'], dict):
            self.errors.append("'mcpServers' must be an object/dictionary")
            return
        
        if len(config['mcpServers']) == 0:
            self.warnings.append("No servers defined in 'mcpServers'")
        
        # Check for unknown top-level keys
        known_keys = {'mcpServers'}
        unknown_keys = set(config.keys()) - known_keys
        if unknown_keys:
            self.warnings.append(f"Unknown top-level keys: {', '.join(unknown_keys)}")
    
    def _validate_servers(self, servers: Dict[str, Any]):
        """Validate server configurations"""
        
        for server_name, server_config in servers.items():
            self._validate_server_name(server_name)
            self._validate_server_config(server_name, server_config)
    
    def _validate_server_name(self, name: str):
        """Validate server name"""
        
        # Check name format
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            self.errors.append(f"Server name '{name}' contains invalid characters. Use only letters, numbers, underscore, and hyphen")
        
        # Check name length
        if len(name) > 50:
            self.warnings.append(f"Server name '{name}' is very long ({len(name)} chars)")
        
        # Check for reserved names
        reserved_names = {'docs', 'openapi.json', 'health', 'metrics'}
        if name.lower() in reserved_names:
            self.warnings.append(f"Server name '{name}' conflicts with reserved endpoint")
    
    def _validate_server_config(self, name: str, config: Dict[str, Any]):
        """Validate individual server configuration"""
        
        if not isinstance(config, dict):
            self.errors.append(f"Server '{name}' configuration must be an object")
            return
        
        # Determine server type
        if 'type' in config:
            self._validate_external_server(name, config)
        else:
            self._validate_command_server(name, config)
    
    def _validate_command_server(self, name: str, config: Dict[str, Any]):
        """Validate command-based server configuration"""
        
        # Check required fields
        if 'command' not in config:
            self.errors.append(f"Server '{name}' missing required 'command' field")
            return
        
        if not isinstance(config['command'], str):
            self.errors.append(f"Server '{name}' 'command' must be a string")
            return
        
        # Validate command exists
        command = config['command']
        if not shutil.which(command):
            self.warnings.append(f"Server '{name}' command '{command}' not found in PATH")
        
        # Validate args
        if 'args' in config:
            if not isinstance(config['args'], list):
                self.errors.append(f"Server '{name}' 'args' must be an array")
            else:
                for i, arg in enumerate(config['args']):
                    if not isinstance(arg, str):
                        self.errors.append(f"Server '{name}' args[{i}] must be a string")
        
        # Validate environment variables
        if 'env' in config:
            if not isinstance(config['env'], dict):
                self.errors.append(f"Server '{name}' 'env' must be an object")
            else:
                for env_key, env_value in config['env'].items():
                    if not isinstance(env_key, str):
                        self.errors.append(f"Server '{name}' env key must be string")
                    if not isinstance(env_value, str):
                        self.errors.append(f"Server '{name}' env['{env_key}'] must be string")
        
        # Check for unknown fields
        known_fields = {'command', 'args', 'env'}
        unknown_fields = set(config.keys()) - known_fields
        if unknown_fields:
            self.warnings.append(f"Server '{name}' has unknown fields: {', '.join(unknown_fields)}")
    
    def _validate_external_server(self, name: str, config: Dict[str, Any]):
        """Validate external server configuration (SSE/HTTP)"""
        
        # Check type
        server_type = config.get('type')
        valid_types = {'sse', 'streamable_http'}
        if server_type not in valid_types:
            self.errors.append(f"Server '{name}' has invalid type '{server_type}'. Must be one of: {', '.join(valid_types)}")
        
        # Check URL
        if 'url' not in config:
            self.errors.append(f"Server '{name}' missing required 'url' field")
        elif not isinstance(config['url'], str):
            self.errors.append(f"Server '{name}' 'url' must be a string")
        else:
            url = config['url']
            if not re.match(r'^https?://', url):
                self.warnings.append(f"Server '{name}' URL should start with http:// or https://")
            
            # Check for environment variable substitution
            if '${' in url:
                env_vars = re.findall(r'\$\{([^}]+)\}', url)
                for var in env_vars:
                    if var not in os.environ:
                        self.warnings.append(f"Server '{name}' URL references undefined environment variable: {var}")
        
        # Validate headers
        if 'headers' in config:
            if not isinstance(config['headers'], dict):
                self.errors.append(f"Server '{name}' 'headers' must be an object")
            else:
                for header_name, header_value in config['headers'].items():
                    if not isinstance(header_name, str):
                        self.errors.append(f"Server '{name}' header name must be string")
                    if not isinstance(header_value, str):
                        self.errors.append(f"Server '{name}' header['{header_name}'] must be string")
                    
                    # Check for environment variables in headers
                    if '${' in header_value:
                        env_vars = re.findall(r'\$\{([^}]+)\}', header_value)
                        for var in env_vars:
                            if var not in os.environ:
                                self.warnings.append(f"Server '{name}' header '{header_name}' references undefined environment variable: {var}")
        
        # Check for unknown fields
        known_fields = {'type', 'url', 'headers'}
        unknown_fields = set(config.keys()) - known_fields
        if unknown_fields:
            self.warnings.append(f"Server '{name}' has unknown fields: {', '.join(unknown_fields)}")
    
    def _validate_common_mcp_servers(self, name: str, config: Dict[str, Any]):
        """Validate common MCP server configurations"""
        
        if 'command' not in config:
            return
        
        command = config['command']
        args = config.get('args', [])
        
        # Memory server validation
        if any('memory' in str(arg) for arg in args):
            self.info.append(f"Server '{name}' appears to be a memory server")
        
        # Time server validation
        if any('time' in str(arg) for arg in args):
            self.info.append(f"Server '{name}' appears to be a time server")
            # Check timezone argument
            timezone_args = [arg for arg in args if '--local-timezone' in str(arg)]
            if timezone_args:
                self.info.append(f"Server '{name}' configured with timezone")
        
        # Filesystem server validation
        if any('filesystem' in str(arg) for arg in args):
            self.info.append(f"Server '{name}' appears to be a filesystem server")
            # Check allowed directories
            allowed_dirs = [arg for arg in args if '--allowed-directories' in str(arg)]
            if not allowed_dirs:
                self.warnings.append(f"Filesystem server '{name}' should specify --allowed-directories for security")
    
    def get_report(self) -> str:
        """Generate validation report"""
        
        report = []
        
        if self.errors:
            report.append("❌ ERRORS:")
            for error in self.errors:
                report.append(f"   • {error}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"   • {warning}")
            report.append("")
        
        if self.info:
            report.append("ℹ️  INFO:")
            for info in self.info:
                report.append(f"   • {info}")
            report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✅ Configuration is valid!")
        elif not self.errors:
            report.append("✅ Configuration is valid (with warnings)")
        else:
            report.append("❌ Configuration has errors and cannot be used")
        
        return "\n".join(report)


def validate_environment_file(env_path: str) -> List[str]:
    """Validate environment file"""
    issues = []
    
    if not os.path.exists(env_path):
        issues.append(f"Environment file not found: {env_path}")
        return issues
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check format
            if '=' not in line:
                issues.append(f"Line {i}: Invalid format (should be KEY=value)")
                continue
            
            key, value = line.split('=', 1)
            
            # Check key format
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                issues.append(f"Line {i}: Key '{key}' should be UPPERCASE_WITH_UNDERSCORES")
            
            # Check for potential security issues
            if 'password' in key.lower() and value in ['password', 'changeme', '123456']:
                issues.append(f"Line {i}: Weak password detected for {key}")
            
            # Check for missing quotes around values with spaces
            if ' ' in value and not (value.startswith('"') and value.endswith('"')):
                issues.append(f"Line {i}: Value with spaces should be quoted")
    
    except Exception as e:
        issues.append(f"Error reading environment file: {e}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate MCPO configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config/multi-server.json
  %(prog)s config/production.json --env env/.env.production
  %(prog)s --check-all
        """
    )
    
    parser.add_argument(
        'config_file',
        nargs='?',
        help='Configuration file to validate'
    )
    
    parser.add_argument(
        '--env',
        help='Environment file to validate'
    )
    
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Check all config files in config/ directory'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # Determine files to check
    config_files = []
    
    if args.check_all:
        config_dir = Path('config')
        if config_dir.exists():
            config_files = list(config_dir.glob('*.json'))
        else:
            print("❌ Config directory not found")
            return 1
    elif args.config_file:
        config_files = [Path(args.config_file)]
    else:
        parser.print_help()
        return 1
    
    # Validate configurations
    all_valid = True
    
    for config_file in config_files:
        print(f"🔍 Validating: {config_file}")
        print("-" * 50)
        
        validator = ConfigValidator()
        is_valid = validator.validate_file(str(config_file))
        
        print(validator.get_report())
        
        if not is_valid:
            all_valid = False
        
        print()
    
    # Validate environment file if specified
    if args.env:
        print(f"🔍 Validating environment file: {args.env}")
        print("-" * 50)
        
        env_issues = validate_environment_file(args.env)
        
        if env_issues:
            print("⚠️  ENVIRONMENT FILE ISSUES:")
            for issue in env_issues:
                print(f"   • {issue}")
            print()
        else:
            print("✅ Environment file is valid!")
            print()
    
    # Summary
    if all_valid:
        print("✅ All configurations are valid!")
        return 0
    else:
        print("❌ Some configurations have errors")
        return 1


if __name__ == '__main__':
    sys.exit(main())