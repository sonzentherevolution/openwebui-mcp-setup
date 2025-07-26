# 🤖 AI-Powered MCP Setup Guide

**The easiest way to add any MCP server to Open Web UI - just ask an AI to do it for you!**

## 🎯 Quick Start

1. **Find any AI assistant** (Claude, ChatGPT, Copilot, etc.)
2. **Share the `agentic-setup.md` file** from this repository with the AI
3. **Use one of the example prompts below**
4. **Follow the AI's custom instructions**

## 📝 Copy-Paste Prompts

### 🔥 **For Specific MCP Servers** (Most Common)

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

**👆 Replace the JSON with your actual MCP server configuration**

### 🤔 **When You Need Help Choosing**

```
I want to add MCP tools to Open Web UI but I'm not sure which ones to choose. Can you help me set this up and recommend the best tools for beginners? Read @agentic-setup.md
```

### 🔗 **From GitHub Repository**

```
I found this MCP server on GitHub: [PASTE_GITHUB_URL_HERE]

Can you help me set it up for Open Web UI? Read @agentic-setup.md
```

### 🐳 **Docker-Specific Setup**

```
I want to set up MCP servers for Open Web UI using Docker. I'm a [beginner/intermediate/advanced] user on [Windows/Mac/Linux]. Can you create a Docker setup for me? Read @agentic-setup.md
```

### 🚀 **Production Setup**

```
I need to set up MCP servers for Open Web UI in a production environment with proper security. Can you help me create a production-ready configuration? Read @agentic-setup.md
```

## 🔍 How to Find MCP Server Configurations

### Method 1: GitHub Repositories (Most Reliable)

1. **Go to any MCP server's GitHub page**
2. **Look for these sections in the README:**
   - "Installation"
   - "Configuration" 
   - "Claude Desktop setup"
   - "Getting Started"

3. **Find a JSON block that looks like this:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/name"]
    }
  }
}
```

4. **Copy the entire JSON block** - that's what you'll give to the AI

### Method 2: Official MCP Server Directory

- **Visit**: [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- **Browse**: Available official servers
- **Click**: On any server to see its setup instructions
- **Copy**: The configuration JSON

### Method 3: NPM Package Search

1. **Search npm** for: `@modelcontextprotocol/server-*`
2. **Click on any package** (e.g., `@modelcontextprotocol/server-filesystem`)
3. **Check the README** for installation instructions
4. **Look for Claude Desktop config** - that's what you need!

### Method 4: Community Collections

- **MCP Hub**: Check community-maintained MCP server lists
- **Reddit/Discord**: Look for MCP server sharing threads
- **Blog posts**: Many developers share their MCP setups

## 🎉 Real Examples

### Example 1: Context7 Documentation Search
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

### Example 2: Filesystem Access
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "--allowed-directories", "./documents"]
    }
  }
}
```

### Example 3: Memory Tool
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

## 🤖 What to Expect from the AI

The AI will ask you questions like:

1. **"What's your experience level?"**
   - Beginner, Intermediate, or Advanced

2. **"What operating system?"**
   - Windows, Mac, Linux, or Docker preference

3. **"Is Open Web UI already running?"**
   - Yes (local/Docker/remote) or No

4. **"How do you prefer to set this up?"**
   - Simple one-command, Docker, step-by-step, or config file

5. **"Any additional preferences?"**
   - Custom ports, API keys, production use, etc.

## ✅ What the AI Will Give You

After answering the questions, the AI will provide:

- ✅ **Converted configuration** (works with Open Web UI)
- ✅ **Exact commands** for your operating system
- ✅ **Docker files** (if you prefer containers)
- ✅ **Step-by-step instructions** with screenshots
- ✅ **Open Web UI URLs** and API keys to use
- ✅ **Testing commands** to verify everything works
- ✅ **Troubleshooting tips** if something goes wrong

## 🎯 Sample AI Conversation

```
You: I want to add this MCP server to Open Web UI... [paste config]

AI: Great! I can help you set that up. What's your experience level with technical setups?

You: Beginner

AI: Perfect! What operating system are you using?

You: Windows

AI: Excellent. Do you already have Open Web UI running?

You: Yes, it's running locally

AI: Great! How would you prefer to set this up?

You: Just give me the simplest way

AI: Perfect! Here's your custom setup:

1. Save this as setup-mcp.bat:
   [AI generates custom script]

2. Double-click the file to run it

3. Add to Open Web UI:
   - Go to Settings → Tools
   - Click "+" to add connection
   - URL: http://localhost:8000
   - Auth: Bearer [AI provides key]
   - Toggle ON and Save

4. Test it by asking: "What time is it?"

Done! Your MCP server is now connected to Open Web UI.
```

## 🚨 Troubleshooting Tips

**If the AI seems confused:**
- Make sure you uploaded the `agentic-setup.md` file
- Double-check your MCP configuration JSON is valid
- Try starting with "Read @agentic-setup.md" in your prompt

**If you can't find MCP configuration:**
- Search GitHub for the MCP server name + "configuration"
- Look for "Claude Desktop" setup instructions
- Check the package's npm page for installation docs

**If the setup doesn't work:**
- Share the error message with the AI
- The AI can help troubleshoot and fix issues
- Try the manual troubleshooting guide in `docs/troubleshooting.md`

## 🎉 Success Stories

**"I had Context7 running in 5 minutes!"**
*- Sarah, Beginner*

**"The AI created a perfect Docker setup for my 5 MCP servers"**
*- Mike, Intermediate*

**"Got a production-ready configuration with security in one conversation"**
*- Lisa, Advanced*

## 🚀 Next Steps

After successful setup:
1. **Test your tools** in Open Web UI
2. **Explore more MCP servers** using this same process
3. **Share your setup** with others
4. **Contribute back** by improving this guide

---

**Ready to get started?** Just pick a prompt above and paste it to any AI with the `agentic-setup.md` file! 🎯