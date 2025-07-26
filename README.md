SEE [AI-SETUP-GUIDE.md](https://github.com/sonzentherevolution/openwebui-mcp-setup/blob/main/agentic-setup.md)

THE FOLLOWING README IS AI GENERATED :)

# 🚀 MCP Server Setup for Open Web UI

**Easily connect powerful MCP tools to Open Web UI with just a few commands!**

This repository provides **simple, step-by-step guides** to add amazing tools to your Open Web UI - like persistent memory, file access, current time, and much more. No complex setup required!

## 🤔 What does this do?

**In simple terms**: This helps you add "superpowers" to your AI chat interface.

**Example tools you can add:**
- 🧠 **Memory Tool**: Your AI remembers things between conversations
- 📁 **File Tool**: Your AI can read and write files on your computer  
- ⏰ **Time Tool**: Your AI always knows the current date and time
- 🌐 **Web Tools**: Your AI can search the internet and access APIs

## 🔧 How it works (the simple version)

1. **MCP Servers** = The individual tools (memory, files, time, etc.)
2. **MCPO** = A simple bridge that makes these tools work with Open Web UI
3. **Open Web UI** = Your chat interface that can now use all these tools

```
🛠️ MCP Tools → 🌉 MCPO Bridge → 💬 Open Web UI
```

## ⚡ Quick Start (Choose Your Adventure!)

### 🎯 **Option 1: I just want to test this quickly!**
Perfect for trying things out:

**Windows:**
```bash
cd examples
time-server.bat
```

**Mac/Linux:**
```bash
cd examples
./time-server.sh
```

Then add `http://localhost:8000` to Open Web UI → Settings → Tools!

### 🔗 **Option 4: I have a specific MCP server from GitHub**
Got an MCP server you want to use? We can convert it!

**Example**: You found this in a GitHub README:
```json
{
  "mcpServers": {
    "github.com/upstash/context7-mcp": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Convert it**:
```bash
cd scripts
python3 convert-mcp-config.py --stdin
# Paste the JSON above, then Ctrl+D
```

**Or just run it directly**:
```bash
uvx mcpo --port 8000 --api-key "your-key" -- npx -y @upstash/context7-mcp@latest
```

Then add `http://localhost:8000` to Open Web UI → Settings → Tools!

### 🐳 **Option 2: I prefer using Docker**
Great for cleaner setups:

```bash
cd docker
docker-compose up -d
```

### 🔧 **Option 3: I want multiple tools**
For the full experience:

**Windows:**
```bash
cd examples
multi-server.bat
```

**Mac/Linux:**
```bash
cd examples
./multi-server.sh
```

## 🤖 AI-Powered Setup (Easiest Way!)

**Let an AI agent do the work for you!** Perfect if you want personalized help or have a specific MCP server in mind.

> 📖 **Full Guide**: Check out [AI-SETUP-GUIDE.md](AI-SETUP-GUIDE.md) for detailed instructions and more example prompts!

### 📋 How to Use AI Setup

1. **Find any AI assistant** (Claude, ChatGPT, etc.)
2. **Upload or share** the `agentic-setup.md` file from this repository
3. **Use one of these prompts**:

#### 🎯 **Prompt Option 1: I have a specific MCP server**
```
I want to add this MCP server to Open Web UI. Here is the configuration:

{
  "mcpServers": {
    "your-server-name": {
      "command": "npx",
      "args": ["-y", "@your/mcp-package"]
    }
  }
}

Can you set this up for me? Read @agentic-setup.md
```

#### 🎯 **Prompt Option 2: I need help choosing**
```
I want to add MCP tools to Open Web UI but I'm not sure which ones to choose. Can you help me set this up? Read @agentic-setup.md
```

#### 🎯 **Prompt Option 3: From GitHub repository**
```
I found this MCP server on GitHub: [paste GitHub URL]
Can you help me set it up for Open Web UI? Read @agentic-setup.md
```

### 🔍 How to Find MCP Configuration

**Method 1: GitHub Repository**
1. Go to any MCP server's GitHub page
2. Look in the README for a JSON block like this:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"]
    }
  }
}
```
3. Copy that entire JSON block

**Method 2: MCP Server Lists**
- Check [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- Browse community MCP collections
- Look for "Installation" or "Configuration" sections

**Method 3: Package Managers**
- Search npm for `@modelcontextprotocol/server-*` packages
- Look at package documentation for setup instructions

### ✨ **What the AI will do for you:**
- ✅ Convert any MCP config to work with Open Web UI
- ✅ Generate the exact commands for your operating system
- ✅ Create Docker configurations if you prefer containers
- ✅ Provide step-by-step setup instructions
- ✅ Give you the exact URLs and API keys to use
- ✅ Help troubleshoot if something goes wrong

### 🎉 **Example AI Conversation**
```
You: "I want to add this MCP server to Open Web UI..."
AI: "Great! What's your experience level with technical setups?"
You: "Beginner"
AI: "Perfect! What operating system are you using?"
You: "Windows"
AI: "Do you have Open Web UI running already?"
You: "Yes, on port 3000"
AI: "Here's your custom setup script... [generates everything for you]"
```

## 📖 Need More Help?

**📚 Detailed guides:**
- **[Open Web UI Setup](OPEN-WEBUI-SETUP.md)** - Exact steps with current UI
- **[Integration Guide](docs/integration-guide.md)** - Complete setup walkthrough
- **[Troubleshooting](docs/troubleshooting.md)** - When things don't work
- **[Security Guide](docs/security.md)** - For production use

**🔧 For developers:**
- **[Configuration Files](config/)** - Advanced server setups
- **[Docker Setups](docker/)** - Container deployments  
- **[Testing Scripts](scripts/)** - Validation and monitoring

## Configuration Options

### Single Server (Command Line)
For running a single MCP server directly:
```bash
uvx mcpo --port 8000 --api-key "your-secret-key" -- uvx mcp-server-time --local-timezone=America/New_York
```

### Multiple Servers (Configuration File)
For running multiple MCP servers, use a configuration file. See `config/` directory for examples.

### Environment Variables
Use `.env` files for secure configuration:
```bash
mcpo --env-path .env --config config.json
```

## Quick Start Guide

1. **Install MCPO**: Choose installation method above
2. **Start a test server**: Use the time server example
3. **Check OpenAPI docs**: Visit `http://localhost:8000/docs`
4. **Configure Open Web UI**: Add the tool server in settings
5. **Test integration**: Try the tools in Open Web UI

## Directory Structure

```
openweb-mcp/
├── README.md                 # This file
├── examples/                 # Quick start examples
│   ├── time-server.sh       # Time server setup
│   └── memory-server.sh     # Memory server setup
├── config/                  # Configuration templates
│   ├── single-server.json   # Single server config
│   ├── multi-server.json    # Multiple servers config
│   └── production.json      # Production-ready config
├── docker/                  # Docker configurations
│   ├── docker-compose.yml   # Basic Docker setup
│   └── docker-compose.prod.yml # Production Docker setup
├── env/                     # Environment configurations
│   ├── .env.example        # Environment variables template
│   └── .env.production      # Production environment
├── scripts/                 # Utility scripts
│   ├── test-connection.sh   # Test MCPO connection
│   └── validate-config.py   # Validate configuration files
└── docs/                   # Additional documentation
    ├── integration-guide.md # Integration with Open Web UI
    ├── troubleshooting.md   # Common issues and solutions
    └── security.md          # Security best practices
```

## Supported MCP Servers

### Built-in Servers
- **mcp-server-time**: Current time and timezone utilities
- **mcp-server-memory**: Persistent memory storage
- **mcp-server-filesystem**: File system operations
- **mcp-server-git**: Git repository operations

### Transport Types
- **stdio**: Standard command-line MCP servers
- **sse**: Server-Sent Events transport
- **streamable_http**: HTTP streaming transport

## Open Web UI Integration

### Adding Tools to Open Web UI

1. **Access Settings**: Go to Open Web UI → Settings → External Tools
2. **Add Tool Server**: Click "Add Tool Server"
3. **Configure URL**: Enter the full path to your tool:
   - Single server: `http://localhost:8000`
   - Multiple servers: `http://localhost:8000/toolname` (e.g., `http://localhost:8000/time`)
4. **Set API Key**: If configured, enter your API key
5. **Test Connection**: Verify the tool loads correctly

### Important Notes
- Each tool requires a separate configuration in Open Web UI
- Use the full path including the tool name for multi-server setups
- Ensure MCPO is running before configuring tools in Open Web UI

## Security Considerations

- Always use API keys in production environments
- Use HTTPS in production deployments
- Limit network access to MCPO ports
- Regularly update MCPO and MCP servers
- Monitor logs for security issues

## Troubleshooting

### Common Issues
1. **Connection refused**: Ensure MCPO is running on the correct port
2. **Tool not found**: Check the URL path and tool name
3. **Authentication failed**: Verify API key configuration
4. **Server startup failed**: Check MCP server dependencies

### Debug Mode
Enable debug logging:
```bash
mcpo --port 8000 --log-level debug -- your_mcp_server_command
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different MCP servers
5. Submit a pull request

## Support

For issues and questions:
- Check the [troubleshooting guide](docs/troubleshooting.md)
- Review Open Web UI documentation
- Check MCPO GitHub issues
- Create an issue in this repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 What Tools Can I Add?

Here's what each tool does in simple terms:

| Tool | What It Does | Example Use |
|------|-------------|-------------|
| 🧠 **Memory** | AI remembers things between chats | "Remember my name is John" → AI recalls this later |
| ⏰ **Time** | Always knows current date/time | "What day is Christmas this year?" |
| 📁 **Files** | Can read/write files on your computer | "Save this code to a file" or "Read my notes.txt" |
| 🌐 **Git** | Works with code repositories | "Show me recent commits" or "Create a new branch" |

## 🤝 Contributing

Found a bug? Have an idea? We'd love your help!
- 🐛 **Report issues** via GitHub Issues
- 💡 **Suggest features** via GitHub Discussions  
- 🔧 **Submit fixes** via Pull Requests
- 📖 **Improve docs** - even small fixes help!

## 🌟 Show Your Support

If this helped you, please ⭐ star the repository to help others find it!

## 📄 License

MIT License - feel free to use this in your own projects!

## 🙏 Acknowledgments

- [Open Web UI](https://github.com/open-webui/open-webui) team for the amazing interface
- [MCPO](https://github.com/open-webui/mcpo) developers for the bridge technology
- MCP community for creating these powerful tools
