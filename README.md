# AI Software Engineering Team - MCP Multi-Agent System

> **Advanced AI-powered software development automation system built on the Model Context Protocol (MCP)**

A sophisticated multi-agent AI system that simulates an entire software engineering team, capable of taking a simple project idea and transforming it into a complete, production-ready software project with full documentation, testing, and deployment configuration.

## Architecture Overview

This system consists of **8 specialized AI agents** working together through an intelligent orchestrator:

- **Product Analyst** - Requirements analysis & user stories
- **Research Engineer** - Web research & best practices
- **Software Architect** - System design & technology stack
- **Technical Lead** - Implementation planning & task breakdown
- **Senior Developer** - Production code implementation
- **QA Engineer** - Testing & quality assurance
- **DevOps Engineer** - CI/CD & deployment infrastructure
- **Documentation Specialist** - Documentation & guides

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js (for MCP Inspector)
- API Keys: Tavily Search, Google Gemini

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ai-software-engineering-team-mcp.git
   cd ai-software-engineering-team-mcp
   ```
2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```
3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
4. **Start the servers**

   ```bash
   # Terminal 1: Start MCP Server
   python server.py

   # Terminal 2: Start FastAPI Server
   python fastapi_server.py
   ```

## API Endpoints

### FastAPI Server (Port 8002)

- `GET /` - Service status and team information
- `GET /health` - Health check with service status
- `GET /tools` - List all available MCP tools
- `GET /project` - Current project status
- `GET /docs` - Interactive API documentation

### MCP Server (Port 8000)

- Direct MCP protocol access for AI tools and clients

## Usage Examples

### Simple Project Request

```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "orchestrator",
      "arguments": {
        "user_request": "Build a todo list app with React and Node.js"
      }
    }
  }'
```

### Complex Project Request

```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "orchestrator",
      "arguments": {
        "user_request": "Build an e-commerce platform with user authentication, product catalog, shopping cart, and payment integration using React, Node.js, and PostgreSQL",
        "execution_mode": "full"
      }
    }
  }'
```

## Available Tools

| Tool                         | Description                                            |
| ---------------------------- | ------------------------------------------------------ |
| `orchestrator`             | Main coordinator that manages the entire team workflow |
| `product_analyst`          | Analyzes requirements and creates user stories         |
| `research_engineer`        | Performs web research and finds best practices         |
| `software_architect`       | Designs system architecture and tech stack             |
| `technical_lead`           | Creates implementation plans and task breakdown        |
| `senior_developer`         | Writes production-ready code                           |
| `qa_engineer`              | Creates comprehensive test suites                      |
| `devops_engineer`          | Sets up CI/CD and deployment configuration             |
| `documentation_specialist` | Creates documentation and guides                       |
| `export_project_files`     | Exports complete project to file system                |
| `team_status`              | Shows current team and project status                  |
| `reset_project`            | Resets project state for new project                   |

## Project Structure

## Configuration

### Environment Variables

```bash
# Required API Keys
TAVILY_API_KEY=your_tavily_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=8000  # MCP Server port
```

### Execution Modes

- `"full"` - All 8 team members (complete project)
- `"planning"` - Analysis, research, architecture only
- `"implementation"` - Adds code implementation
- `"deployment"` - Adds DevOps configuration
- `"custom"` - AI decides based on complexity

## Testing

### Test the MCP Server

```bash
# Check server status
curl http://localhost:8000/health

# List available tools
curl http://localhost:8002/tools
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

## Features

- **End-to-End Automation** - From idea to deployable code
- **Multi-Agent Coordination** - 8 specialized AI agents
- **Intelligent Decision Making** - Adapts workflow based on complexity
- **Production-Ready Output** - Generates actual, usable code
- **Dual Protocol Support** - Both MCP and REST API access
- **Live Research Integration** - Real-time web search capabilities
- **Complete Project Export** - Full file system generation
- **Interactive Documentation** - Built-in API docs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by [Google Gemini](https://ai.google.dev/) and [Tavily Search](https://tavily.com/)
- FastAPI integration for REST API access

## Support

- Email: [your-email@example.com]
- Issues: [GitHub Issues](https://github.com/yourusername/ai-software-engineering-team-mcp/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ai-software-engineering-team-mcp/discussions)

---

**Made with care by the AI Software Engineering Team**
