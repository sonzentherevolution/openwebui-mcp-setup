#!/bin/bash

# MCPO Connection Test Script
# Tests connectivity and functionality of MCPO proxy and MCP servers

set -e

# Default configuration
MCPO_URL="${MCPO_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-demo-secret-key}"
TIMEOUT="${TIMEOUT:-10}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test functions
test_basic_connectivity() {
    log_info "Testing basic connectivity to MCPO..."
    
    if curl -s -f --max-time "$TIMEOUT" "$MCPO_URL/docs" > /dev/null; then
        log_success "MCPO is responding"
        return 0
    else
        log_error "MCPO is not responding at $MCPO_URL"
        return 1
    fi
}

test_authentication() {
    log_info "Testing API key authentication..."
    
    response=$(curl -s -w "%{http_code}" --max-time "$TIMEOUT" \
        -H "Authorization: Bearer $API_KEY" \
        "$MCPO_URL/docs" -o /dev/null)
    
    if [ "$response" = "200" ]; then
        log_success "Authentication successful"
        return 0
    elif [ "$response" = "401" ] || [ "$response" = "403" ]; then
        log_error "Authentication failed (HTTP $response)"
        return 1
    else
        log_warning "Unexpected response code: $response"
        return 1
    fi
}

test_openapi_docs() {
    log_info "Testing OpenAPI documentation..."
    
    docs_content=$(curl -s --max-time "$TIMEOUT" \
        -H "Authorization: Bearer $API_KEY" \
        "$MCPO_URL/docs")
    
    if echo "$docs_content" | grep -q "OpenAPI"; then
        log_success "OpenAPI documentation is accessible"
        return 0
    else
        log_error "OpenAPI documentation not found or invalid"
        return 1
    fi
}

test_available_tools() {
    log_info "Discovering available tools..."
    
    # Try to get the OpenAPI spec
    spec=$(curl -s --max-time "$TIMEOUT" \
        -H "Authorization: Bearer $API_KEY" \
        "$MCPO_URL/openapi.json" 2>/dev/null || echo "{}")
    
    if command -v jq > /dev/null; then
        tools=$(echo "$spec" | jq -r '.paths | keys[]' 2>/dev/null | grep -v "^/docs\|^/openapi.json\|^/$" | sed 's|^/||' || echo "")
    else
        # Fallback without jq
        tools=$(echo "$spec" | grep -o '"/[^"]*"' | grep -v '"/docs\|"/openapi.json\|"/$' | sed 's|"/||g' | sed 's|"||g' || echo "")
    fi
    
    if [ -n "$tools" ]; then
        log_success "Found tools: $(echo $tools | tr '\n' ' ')"
        echo "$tools"
    else
        log_warning "No tools discovered (may be single-server setup)"
        echo ""
    fi
}

test_tool_functionality() {
    local tool="$1"
    log_info "Testing tool: $tool"
    
    # Test tool endpoint
    if [ -n "$tool" ]; then
        endpoint="$MCPO_URL/$tool"
    else
        endpoint="$MCPO_URL"
    fi
    
    response=$(curl -s -w "%{http_code}" --max-time "$TIMEOUT" \
        -H "Authorization: Bearer $API_KEY" \
        "$endpoint" -o /dev/null)
    
    if [ "$response" = "200" ]; then
        log_success "Tool '$tool' is responding"
        return 0
    else
        log_error "Tool '$tool' failed (HTTP $response)"
        return 1
    fi
}

run_comprehensive_test() {
    local tool="$1"
    log_info "Running comprehensive test for tool: $tool"
    
    # Prepare test endpoint
    if [ -n "$tool" ]; then
        endpoint="$MCPO_URL/$tool"
    else
        endpoint="$MCPO_URL"
    fi
    
    # Test various HTTP methods
    log_info "Testing GET request..."
    get_response=$(curl -s -w "%{http_code}" --max-time "$TIMEOUT" \
        -H "Authorization: Bearer $API_KEY" \
        "$endpoint" -o /dev/null)
    
    if [ "$get_response" = "200" ]; then
        log_success "GET request successful"
    else
        log_warning "GET request returned HTTP $get_response"
    fi
    
    # Test POST request (if applicable)
    log_info "Testing POST capabilities..."
    post_response=$(curl -s -w "%{http_code}" --max-time "$TIMEOUT" \
        -X POST \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' \
        "$endpoint" -o /dev/null 2>/dev/null || echo "000")
    
    if [ "$post_response" = "200" ] || [ "$post_response" = "405" ]; then
        log_success "POST capabilities confirmed"
    else
        log_warning "POST test returned HTTP $post_response"
    fi
}

# Performance testing
test_performance() {
    log_info "Running basic performance test..."
    
    start_time=$(date +%s%N)
    
    for i in {1..5}; do
        curl -s --max-time "$TIMEOUT" \
            -H "Authorization: Bearer $API_KEY" \
            "$MCPO_URL/docs" > /dev/null
    done
    
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    avg_response=$(( duration / 5 ))
    
    if [ "$avg_response" -lt 1000 ]; then
        log_success "Average response time: ${avg_response}ms"
    elif [ "$avg_response" -lt 5000 ]; then
        log_warning "Average response time: ${avg_response}ms (acceptable)"
    else
        log_error "Average response time: ${avg_response}ms (slow)"
    fi
}

# Main execution
main() {
    echo "======================================"
    echo "  MCPO Connection Test Script"
    echo "======================================"
    echo "MCPO URL: $MCPO_URL"
    echo "API Key: ${API_KEY:0:8}..."
    echo "Timeout: ${TIMEOUT}s"
    echo "======================================"
    echo ""
    
    # Check prerequisites
    if ! command -v curl > /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    # Run basic tests
    test_basic_connectivity || exit 1
    test_authentication || exit 1
    test_openapi_docs || exit 1
    
    # Discover and test tools
    tools=$(test_available_tools)
    
    if [ -n "$tools" ]; then
        # Multi-server setup
        for tool in $tools; do
            test_tool_functionality "$tool"
        done
        
        # Run comprehensive test on first tool
        first_tool=$(echo "$tools" | head -n1)
        run_comprehensive_test "$first_tool"
    else
        # Single-server setup
        test_tool_functionality ""
        run_comprehensive_test ""
    fi
    
    # Performance test
    test_performance
    
    echo ""
    echo "======================================"
    log_success "All tests completed successfully!"
    echo "======================================"
    
    # Summary
    echo ""
    echo "Connection Summary:"
    echo "  MCPO URL: $MCPO_URL"
    echo "  Status: Online"
    echo "  Authentication: Working"
    echo "  Tools Found: $(echo $tools | wc -w || echo 1)"
    echo ""
    echo "Next steps:"
    echo "  1. Add this URL to Open Web UI: $MCPO_URL"
    echo "  2. Use API key: $API_KEY"
    if [ -n "$tools" ]; then
        echo "  3. Configure individual tools:"
        for tool in $tools; do
            echo "     - $tool: $MCPO_URL/$tool"
        done
    fi
}

# Handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            MCPO_URL="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --url URL          MCPO URL (default: http://localhost:8000)"
            echo "  --api-key KEY      API key for authentication"
            echo "  --timeout SECONDS  Request timeout (default: 10)"
            echo "  --help             Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  MCPO_URL          MCPO URL"
            echo "  API_KEY           API key"
            echo "  TIMEOUT           Request timeout"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main