#!/usr/bin/env python3
"""
Universal MCP Configuration Converter

Converts standard MCP server configurations to MCPO-compatible format.
Handles various formats and provides guidance for Open Web UI integration.
"""

import json
import sys
import argparse
import re
from typing import Dict, List, Any, Optional

class MCPConfigConverter:
    """Convert MCP configurations to MCPO format"""
    
    def __init__(self):
        self.converted_servers = {}
        self.warnings = []
        self.info = []
    
    def convert_standard_config(self, mcp_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert standard MCP configuration to MCPO format"""
        
        if 'mcpServers' not in mcp_config:
            raise ValueError("Invalid MCP configuration: missing 'mcpServers' key")
        
        servers = mcp_config['mcpServers']
        mcpo_config = {"mcpServers": {}}
        
        for server_name, server_config in servers.items():
            converted = self._convert_single_server(server_name, server_config)
            if converted:
                # Clean up server name for MCPO (remove domain, special chars)
                clean_name = self._clean_server_name(server_name)
                mcpo_config['mcpServers'][clean_name] = converted
        
        return mcpo_config
    
    def _convert_single_server(self, name: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a single server configuration"""
        
        if config.get('disabled', False):
            self.info.append(f"Skipping disabled server: {name}")
            return None
        
        if 'command' not in config:
            self.warnings.append(f"Server '{name}' missing command field")
            return None
        
        command = config['command']
        args = config.get('args', [])
        
        # Handle Windows command wrappers
        if command.lower() in ['cmd', 'cmd.exe']:
            command, args = self._unwrap_windows_command(args)
        
        # Handle PowerShell wrappers
        if command.lower() in ['powershell', 'pwsh']:
            command, args = self._unwrap_powershell_command(args)
        
        converted = {
            'command': command,
            'args': args
        }
        
        # Add environment variables if present
        if 'env' in config:
            converted['env'] = config['env']
        
        # Note special configurations
        if 'autoApprove' in config and config['autoApprove']:
            self.info.append(f"Server '{name}' has autoApprove settings - may need manual approval in Open Web UI")
        
        return converted
    
    def _unwrap_windows_command(self, args: List[str]) -> tuple[str, List[str]]:
        """Unwrap Windows cmd.exe wrappers"""
        if not args:
            return 'cmd', []
        
        # Remove /c flag
        if args[0].lower() in ['/c', '-c']:
            args = args[1:]
        
        if not args:
            return 'cmd', []
        
        # Extract actual command
        actual_command = args[0]
        actual_args = args[1:]
        
        return actual_command, actual_args
    
    def _unwrap_powershell_command(self, args: List[str]) -> tuple[str, List[str]]:
        """Unwrap PowerShell command wrappers"""
        if not args:
            return 'powershell', []
        
        # Look for -Command flag
        if len(args) >= 2 and args[0].lower() in ['-command', '-c']:
            command_string = args[1]
            # Parse the command string (basic parsing)
            parts = command_string.split()
            if parts:
                return parts[0], parts[1:]
        
        return 'powershell', args
    
    def _clean_server_name(self, name: str) -> str:
        """Clean server name for use as MCPO route"""
        # Remove common prefixes
        name = re.sub(r'^(github\.com/|gitlab\.com/|mcp-server-)', '', name)
        
        # Replace invalid characters with underscores
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        return name or 'server'
    
    def convert_from_repository_readme(self, readme_text: str) -> Dict[str, Any]:
        """Extract MCP configuration from repository README"""
        
        # Look for JSON blocks containing mcpServers
        json_blocks = re.findall(r'```(?:json)?\s*(\{[^`]*"mcpServers"[^`]*\})\s*```', 
                                readme_text, re.MULTILINE | re.DOTALL)
        
        if not json_blocks:
            raise ValueError("No MCP configuration found in README")
        
        # Use the first valid JSON block
        for block in json_blocks:
            try:
                config = json.loads(block)
                return self.convert_standard_config(config)
            except json.JSONDecodeError:
                continue
        
        raise ValueError("No valid MCP configuration JSON found")
    
    def generate_usage_instructions(self, mcpo_config: Dict[str, Any], 
                                  base_url: str = "http://localhost:8000") -> str:
        """Generate usage instructions for Open Web UI"""
        
        instructions = []
        instructions.append("🚀 Setup Instructions for Open Web UI")
        instructions.append("=" * 45)
        instructions.append("")
        
        # MCPO startup command
        instructions.append("1. Start MCPO with this configuration:")
        instructions.append("```bash")
        instructions.append("# Save the config to a file")
        instructions.append("cat > mcp-config.json << 'EOF'")
        instructions.append(json.dumps(mcpo_config, indent=2))
        instructions.append("EOF")
        instructions.append("")
        instructions.append("# Start MCPO")
        instructions.append("uvx mcpo --port 8000 --api-key 'your-secure-key' --config mcp-config.json")
        instructions.append("```")
        instructions.append("")
        
        # Open Web UI configuration
        instructions.append("2. Add tools to Open Web UI:")
        instructions.append("")
        servers = mcpo_config.get('mcpServers', {})
        
        for server_name in servers.keys():
            tool_url = f"{base_url}/{server_name}"
            instructions.append(f"   📊 **{server_name.title()} Tool**:")
            instructions.append(f"   - Name: {server_name.title()}")
            instructions.append(f"   - URL: {tool_url}")
            instructions.append(f"   - API Key: your-secure-key")
            instructions.append("")
        
        # Testing
        instructions.append("3. Test the setup:")
        instructions.append("```bash")
        instructions.append("# Test connectivity")
        instructions.append(f"curl -H 'Authorization: Bearer your-secure-key' {base_url}/docs")
        instructions.append("")
        instructions.append("# Test specific tools")
        for server_name in servers.keys():
            instructions.append(f"curl -H 'Authorization: Bearer your-secure-key' {base_url}/{server_name}")
        instructions.append("```")
        instructions.append("")
        
        # Warnings and info
        if self.warnings:
            instructions.append("⚠️ Warnings:")
            for warning in self.warnings:
                instructions.append(f"   - {warning}")
            instructions.append("")
        
        if self.info:
            instructions.append("ℹ️ Additional Information:")
            for info in self.info:
                instructions.append(f"   - {info}")
            instructions.append("")
        
        return "\n".join(instructions)


def main():
    parser = argparse.ArgumentParser(
        description="Convert MCP configurations to MCPO format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert from standard MCP config file
  %(prog)s --input mcp-config.json
  
  # Convert from README text
  %(prog)s --readme README.md
  
  # Convert from clipboard (paste JSON)
  %(prog)s --stdin
  
  # Generate with custom base URL
  %(prog)s --input config.json --base-url https://my-server.com
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', help='Input MCP configuration file')
    input_group.add_argument('--readme', help='README file containing MCP config')
    input_group.add_argument('--stdin', action='store_true', help='Read JSON from stdin')
    
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--base-url', default='http://localhost:8000', 
                       help='Base URL for MCPO server')
    parser.add_argument('--instructions', action='store_true',
                       help='Generate setup instructions')
    parser.add_argument('--config-only', action='store_true',
                       help='Output only the MCPO config JSON')
    
    args = parser.parse_args()
    
    converter = MCPConfigConverter()
    
    try:
        # Read input
        if args.input:
            with open(args.input, 'r') as f:
                mcp_config = json.load(f)
            mcpo_config = converter.convert_standard_config(mcp_config)
        
        elif args.readme:
            with open(args.readme, 'r') as f:
                readme_text = f.read()
            mcpo_config = converter.convert_from_repository_readme(readme_text)
        
        elif args.stdin:
            print("Paste your MCP configuration JSON (Press Ctrl+D when done):")
            stdin_text = sys.stdin.read()
            mcp_config = json.loads(stdin_text)
            mcpo_config = converter.convert_standard_config(mcp_config)
        
        # Generate output
        if args.config_only:
            output = json.dumps(mcpo_config, indent=2)
        elif args.instructions:
            output = converter.generate_usage_instructions(mcpo_config, args.base_url)
        else:
            # Default: both config and instructions
            config_json = json.dumps(mcpo_config, indent=2)
            instructions = converter.generate_usage_instructions(mcpo_config, args.base_url)
            output = f"MCPO Configuration:\n{config_json}\n\n{instructions}"
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Output written to {args.output}")
        else:
            print(output)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())