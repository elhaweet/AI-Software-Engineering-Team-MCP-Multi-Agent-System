import contextlib
from fastapi import FastAPI
import os
import uvicorn
from datetime import datetime

# Import your existing MCP server
from server import mcp, TAVILY_API_KEY, GEMINI_AVAILABLE, project_state

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the MCP server lifecycle"""
    async with mcp.session_manager.run():
        yield

# Create FastAPI app
app = FastAPI(
    title="AI Software Engineering Team",
    description="Advanced AI-powered software development automation system with FastAPI integration",
    version="2.0.0",
    lifespan=lifespan
)

# Mount the MCP server
app.mount("/mcp", mcp.streamable_http_app())

@app.get("/")
async def root():
    return {
        "service": "AI Software Engineering Team",
        "version": "2.0.0",
        "status": "running",
        "mcp_endpoint": "/mcp",
        "team_members": 8,
        "current_project": project_state.get("current_project"),
        "services": {
            "tavily_search": "✅ Connected" if TAVILY_API_KEY else "❌ Not configured",
            "gemini_ai": "✅ Connected" if GEMINI_AVAILABLE else "❌ Not available"
        },
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "tools": "/tools",
            "project_status": "/project",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mcp_server": "running",
            "tavily_api": "connected" if TAVILY_API_KEY else "not_configured",
            "gemini_ai": "connected" if GEMINI_AVAILABLE else "not_available"
        }
    }

@app.get("/project")
async def get_project_status():
    """Get current project status via REST API"""
    return {
        "current_project": project_state.get("current_project"),
        "has_requirements": project_state.get("requirements") is not None,
        "has_architecture": project_state.get("architecture") is not None,
        "has_implementation_plan": project_state.get("implementation_plan") is not None,
        "code_modules_count": len(project_state.get("code_modules", {})),
        "has_deployment_plan": project_state.get("deployment_plan") is not None,
        "available_modules": list(project_state.get("code_modules", {}).keys())
    }

@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "total_tools": len(mcp._tools),
        "tools": [
            {
                "name": name,
                "description": tool.description or "No description available"
            }
            for name, tool in mcp._tools.items()
        ]
    }

# Force a specific port to avoid conflicts
PORT = int(os.environ.get("PORT", 8002))

if __name__ == "__main__":
    # Override any environment PORT setting for this server
    PORT = 8002
    print("\n" + "="*80)
    print("🚀 AI SOFTWARE ENGINEERING TEAM - FASTAPI SERVER")
    print("="*80)
    print(f"📡 Port: {PORT}")
    print(f"🌐 Endpoints:")
    print(f"  • Root: http://localhost:{PORT}/")
    print(f"  • MCP: http://localhost:{PORT}/mcp")
    print(f"  • Health: http://localhost:{PORT}/health")
    print(f"  • Project: http://localhost:{PORT}/project")
    print(f"  • Tools: http://localhost:{PORT}/tools")
    print(f"  • API Docs: http://localhost:{PORT}/docs")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)