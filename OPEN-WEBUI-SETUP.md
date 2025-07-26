# 🔗 How to Add MCP Tools to Open Web UI

**Based on the actual Open Web UI interface - step by step with screenshots!**

## 📍 Exact Steps (Updated for Current UI)

### Step 1: Open Your Settings
- Go to your Open Web UI (usually `http://localhost:3000` or `http://localhost:8080`)
- Click the **⚙️ Settings** gear icon (bottom left corner)

### Step 2: Navigate to Tools
- In the Settings menu, click **"Tools"** (not "External Tools")
- You'll see your current tool connections listed

### Step 3: Add New Tool Connection
- Click the **"+"** button to add a new connection
- This opens the "Edit Connection" dialog

### Step 4: Fill in the Connection Details
Based on the interface shown:

**URL Field:**
- Enter your MCPO server URL: `http://localhost:8000`
- Open Web UI automatically appends `/openapi.json` to check the API

**Auth Section:**
- Select **"Bearer"** from the dropdown (this is the authentication type)
- In the text field, enter your API key (e.g., `context7-secret-key`)

**Toggle Switch:**
- Make sure the toggle switch is **ON** (green) to enable the tool

### Step 5: Save the Connection
- Click the **"Save"** button
- The tool should now appear in your tools list

### Step 6: Test Your Tool
- Go back to your chat interface
- Try asking something that would use your tool
- Example: *"What time is it?"* (for time server) or *"Search for React documentation"* (for Context7)

## 🎯 **Important Notes**

### **No Name Required**
- You don't need to provide a name for the tool
- Open Web UI automatically detects the tool name from the API

### **URL Format**  
- Use just the base URL: `http://localhost:8000`
- Don't add `/docs` or any other path
- Open Web UI automatically adds `/openapi.json` to discover the API

### **Authentication**
- Always use **"Bearer"** authentication type
- Enter your API key in the text field (without "Bearer " prefix)
- This must match the API key you used when starting MCPO

### **Multi-Server Setup**
If you have multiple tools in one MCPO instance:
- **Single Connection**: Use `http://localhost:8000` and Open Web UI will discover all tools
- **Separate Connections**: You can also add each tool individually:
  - Memory: `http://localhost:8000/memory`  
  - Time: `http://localhost:8000/time`
  - Context7: `http://localhost:8000/context7`

## 🔧 **Common Connection Settings**

### **Local MCPO Server**
```
URL: http://localhost:8000
Auth: Bearer
Key: your-api-key
```

### **Docker MCPO (same network)**
```
URL: http://mcpo:8000
Auth: Bearer  
Key: your-api-key
```

### **Remote MCPO Server**
```
URL: https://your-server.com:8000
Auth: Bearer
Key: your-secure-api-key
```

## ❌ **Troubleshooting**

### **Connection Failed**
- ✅ Check that MCPO is running: `curl http://localhost:8000/docs`
- ✅ Verify the URL is correct (no extra paths)
- ✅ Ensure the API key matches exactly
- ✅ Check that the toggle switch is ON (green)

### **Tool Not Working**
- ✅ Test the tool directly: `curl -H "Authorization: Bearer your-key" http://localhost:8000`
- ✅ Check MCPO logs for errors
- ✅ Try refreshing the Open Web UI page
- ✅ Verify the MCP server is working properly

### **Multiple Tools Not Detected**
- ✅ Use the base URL (`http://localhost:8000`) not individual tool paths
- ✅ Check that your MCPO configuration has multiple servers defined
- ✅ Verify each MCP server is starting successfully

## 🎉 **Success!**

Once connected, you should see:
- ✅ The tool appears in your Tools list
- ✅ The toggle switch stays green
- ✅ No error messages in the connection dialog
- ✅ The AI can use the tool in conversations

**Test it by asking questions that would use your specific tool!**

---

*This guide matches the current Open Web UI interface. If the UI changes, please update this documentation.*