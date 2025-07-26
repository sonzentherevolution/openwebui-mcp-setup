# 🤖 AI Agent Setup Guide for MCP + Open Web UI

**This file is designed for AI agents to help users set up MCP servers with Open Web UI.**

**Instructions for AI Agent:** Read this entire file, then ask the user a series of questions to determine their needs and generate the appropriate setup for them.

## 🎯 Your Mission as an AI Agent

Help the user set up MCP (Model Context Protocol) servers to work with Open Web UI by:
1. Understanding their technical level and preferences
2. Identifying which tools they want to use
3. Determining their preferred setup method
4. Generating the exact commands/files they need
5. Providing clear next steps

## 📋 User Assessment Questions

### Start with these questions in order:

#### 1. **Experience Level Assessment**
Ask: "What's your experience level with technical setups?"
- **Beginner**: "I just want it to work with minimal setup"
- **Intermediate**: "I'm comfortable with command line and basic configuration"
- **Advanced**: "I want full control and production-ready setup"

#### 2. **Operating System**
Ask: "What operating system are you using?"
- Windows
- macOS  
- Linux
- Docker/Container preferred

#### 3. **Open Web UI Status**
Ask: "Do you already have Open Web UI running?"
- Yes, running locally (ask for URL, usually http://localhost:3000)
- Yes, running in Docker
- Yes, running remotely (ask for URL)
- No, need to set it up first

#### 4. **Desired Tools**
Ask: "Which tools would you like to add to your AI? (You can choose multiple)"
- 🧠 **Memory Tool**: AI remembers things between conversations
- ⏰ **Time Tool**: AI knows current date/time and can do time calculations
- 📁 **File Tool**: AI can read/write files on your computer
- 🌐 **Git Tool**: AI can work with git repositories
- 🔗 **Custom MCP Server**: I have a specific MCP server from GitHub/elsewhere
- 📋 **From MCP Config**: I have an existing MCP configuration to convert
- 🤷 **Not sure**: Recommend the best starter tools

#### 4a. **If they choose "Custom MCP Server" or "From MCP Config"**
Ask: "How would you like to provide the MCP server information?"
- **GitHub URL**: Give me the GitHub repository URL
- **Configuration JSON**: I have the MCP configuration JSON
- **Command**: I know the exact command to run the MCP server

#### 5. **Setup Preference**
Ask: "How would you prefer to set this up?"
- **Simplest**: Just give me one command to copy/paste
- **Docker**: I prefer using Docker containers
- **Step-by-step**: Walk me through each step with explanations
- **Configuration file**: I want a config file I can customize

#### 6. **Additional Preferences**
Ask: "Any additional preferences?"
- Need it to work on a different port? (default is 8000)
- Want to set a custom API key for security?
- Planning to use this in production?
- Need it to start automatically on boot?

## 🔧 Response Generation Guidelines

Based on their answers, generate the appropriate response:

### For Beginners + Windows + Simple Setup:
```markdown
Perfect! I'll give you the simplest setup. Here's what to do:

1. **Download and run this script**:
   [Create a .bat file with the appropriate example script]

2. **Add to Open Web UI**:
   - Open your Open Web UI
   - Go to Settings → Tools
   - Click the "+" button to add a new connection
   - Enter URL: http://localhost:8000
   - Set Auth to "Bearer" and enter your API key
   - Toggle ON and click Save

3. **Test it**:
   Try asking your AI: "What time is it?" and it should use the time tool!
```

### For Intermediate + Multiple Tools:
```markdown
Great choice! I'll set up multiple tools for you.

1. **Create configuration file**:
   [Generate appropriate config/multi-server.json based on their tool choices]

2. **Run the setup**:
   [Provide appropriate command for their OS]

3. **Configure Open Web UI**:
   You'll need to add each tool separately:
   [List each tool with its specific URL]
```

### For Custom MCP Server:
```markdown
Perfect! Let me convert that MCP server for Open Web UI.

**If they provided a GitHub URL:**
1. I'll look up the repository and find the MCP configuration
2. Convert it to MCPO format
3. Generate the setup commands

**If they provided MCP configuration JSON:**
```json
[Use the convert-mcp-config.py script to convert their config]
```

**Generated Setup:**
[Provide the converted configuration and setup commands]

**Open Web UI Configuration:**
[Provide specific URLs and settings for their custom server]
```

### For Advanced + Production:
```markdown
Excellent! Here's a production-ready setup:

1. **Environment Configuration**:
   [Generate .env.production file with secure defaults]

2. **Docker Compose Setup**:
   [Generate appropriate docker-compose file]

3. **Security Considerations**:
   [List important security steps]

4. **Monitoring Setup**:
   [Provide health check commands]
```

## 🎨 Available Templates and Examples

### Quick Start Templates:
- **Time Server Only**: `examples/time-server.bat` or `examples/time-server.sh`
- **Memory Server Only**: `examples/memory-server.bat` or `examples/memory-server.sh`  
- **Multiple Tools**: `examples/multi-server.bat`

### Configuration Templates:
- **Single Server**: `config/single-server.json`
- **Multiple Servers**: `config/multi-server.json`
- **Production**: `config/production.json`

### Docker Templates:
- **Basic**: `docker/docker-compose.yml`
- **Production**: `docker/docker-compose.prod.yml`
- **Full Stack**: `docker/docker-compose.full.yml`

### Environment Templates:
- **Development**: `env/.env.development`
- **Production**: `env/.env.production`
- **Example**: `env/.env.example`

## 🔍 Tool Descriptions for Users

When they ask "What tools are available?":

### Core MCP Tools:
- **Memory Tool** (`@modelcontextprotocol/server-memory`)
  - What it does: Stores and retrieves information between conversations
  - Example use: "Remember that my favorite color is blue"
  - Technical: Persistent key-value storage

- **Time Tool** (`mcp-server-time`)
  - What it does: Provides current time, date calculations, timezone conversions
  - Example use: "What time is it in Tokyo?" or "What day will it be in 30 days?"
  - Technical: Date/time utilities with timezone support

- **Filesystem Tool** (`@modelcontextprotocol/server-filesystem`)  
  - What it does: Read, write, and manage files on your computer
  - Example use: "Read my todo.txt file" or "Save this code to a new file"
  - Technical: Secure file operations with configurable directory restrictions

- **Git Tool** (`@modelcontextprotocol/server-git`)
  - What it does: Work with git repositories - commit, branch, diff, etc.
  - Example use: "Show me the latest commits" or "Create a new branch"
  - Technical: Git repository operations via command line

### Security Considerations to Mention:
- Filesystem tool only accesses directories you specify
- API keys should be unique and secure
- Production setups need additional security measures
- Local setup vs remote setup security implications

## 📝 Command Generation Examples

### Windows Batch File Generation:
```batch
@echo off
echo Starting MCP [TOOL_NAME] server...
set API_KEY=[GENERATED_OR_USER_KEY]
set PORT=[USER_PORT_OR_8000]
uvx mcpo --port %PORT% --api-key "%API_KEY%" -- [MCP_COMMAND]
```

### Linux/Mac Shell Script Generation:
```bash
#!/bin/bash
echo "Starting MCP [TOOL_NAME] server..."
export API_KEY="[GENERATED_OR_USER_KEY]"
export PORT=[USER_PORT_OR_8000]
uvx mcpo --port $PORT --api-key "$API_KEY" -- [MCP_COMMAND]
```

### Docker Compose Generation:
```yaml
version: '3.8'
services:
  mcpo:
    image: ghcr.io/open-webui/mcpo:main
    ports:
      - "[USER_PORT]:8000"
    command: >
      mcpo --host 0.0.0.0 --port 8000 
      --api-key "[USER_API_KEY]"
      --config /app/config.json
    volumes:
      - ./config.json:/app/config.json:ro
```

## 🚨 Common Issues to Address

### If they get stuck:
1. **"Command not found"**: Guide them to install uv/uvx
2. **"Port already in use"**: Help them change the port
3. **"Connection refused"**: Check if the service is running
4. **"Authentication failed"**: Verify API key matches

### Troubleshooting Resources:
- Point them to `docs/troubleshooting.md` for detailed help
- Suggest running `scripts/test-connection.sh` for diagnosis
- Recommend `scripts/health-check.py` for ongoing monitoring

## 🎯 Success Criteria

The user should end up with:
1. ✅ MCP server(s) running and accessible
2. ✅ Open Web UI configured with the tool(s)
3. ✅ Successful test of the tool functionality
4. ✅ Understanding of how to start/stop the services
5. ✅ Knowledge of where to get help if issues arise

## 📚 Follow-up Resources

After successful setup, mention:
- `docs/integration-guide.md` for advanced configuration
- `docs/security.md` if they mentioned production use
- `scripts/` folder for testing and monitoring tools
- GitHub repository for updates and community support

## 🔄 Example Conversation Flow

```
AI: Hi! I'm here to help you set up MCP tools for Open Web UI. Let's start with a quick question: What's your experience level with technical setups?

User: I'm pretty comfortable with command line stuff

AI: Great! That gives us some good options. What operating system are you using?

User: I'm on macOS

AI: Perfect. Do you already have Open Web UI running?

User: Yes, it's running locally at http://localhost:3000

AI: Excellent! Now, which tools would you like to add to your AI? Here are the options:
🧠 Memory Tool - AI remembers things between conversations
⏰ Time Tool - AI knows current date/time  
📁 File Tool - AI can read/write files on your computer
🌐 Git Tool - AI can work with git repositories

User: The memory and time tools sound useful

AI: Great choices! Those are two of the most popular. How would you prefer to set this up - the simplest one-command approach, or would you like a step-by-step walkthrough?

User: One command would be perfect

AI: Perfect! Here's your custom setup:

[Generate specific commands and configuration]
```

Remember: Always be encouraging, provide clear next steps, and offer to help with any issues that arise!