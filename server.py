from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict, List, Optional
import os
import json
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
import shutil

# Load environment variables
load_dotenv()

# Check for required API keys
if "TAVILY_API_KEY" not in os.environ:
    raise Exception("TAVILY_API_KEY environment variable not set")

# Initialize Tavily client
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
tavily_client = TavilyClient(TAVILY_API_KEY)

# Initialize Gemini
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        GEMINI_AVAILABLE = True
        print("✅ Gemini initialized successfully")
    else:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
except Exception as e:
    print(f"❌ Gemini initialization failed: {str(e)}")
    GEMINI_ERROR = str(e)

PORT = os.environ.get("PORT", 8000)

# Create an MCP server
mcp = FastMCP("ai-software-engineering-team", host="0.0.0.0", port=PORT)

# Project state management (in-memory for this session)
project_state = {
    "current_project": None,
    "requirements": None,
    "architecture": None,
    "tech_stack": None,
    "implementation_plan": None,
    "code_modules": {},
    "testing_results": None,
    "deployment_plan": None
}

# =============================================================================
# TEAM MEMBER 1: PRODUCT ANALYST
# =============================================================================

@mcp.tool()
def product_analyst(user_request: str, additional_context: str = "") -> str:
    """
    🎯 Product Analyst - Analyzes user requirements and creates detailed product specifications.
    
    This agent:
    - Understands user needs and business goals
    - Creates user stories and acceptance criteria
    - Identifies core features and MVP scope
    - Defines success metrics
    
    Args:
        user_request: The user's application idea or requirements
        additional_context: Any additional context or constraints
    
    Returns:
        Detailed product analysis and requirements document
    """
    if not GEMINI_AVAILABLE:
        return "❌ Product Analyst requires Gemini AI"
    
    analyst_prompt = f"""
    You are an expert Product Analyst on an AI software engineering team.
    
    USER REQUEST:
    {user_request}
    
    ADDITIONAL CONTEXT:
    {additional_context if additional_context else "None provided"}
    
    Analyze this request and create a comprehensive product specification:
    
    1. 🎯 **PROJECT OVERVIEW**
       - Project name suggestion
       - Brief description (2-3 sentences)
       - Target users/audience
       - Main problem being solved
    
    2. 📋 **CORE REQUIREMENTS**
       - Must-have features (MVP)
       - Should-have features (Phase 2)
       - Nice-to-have features (Future)
    
    3. 👥 **USER STORIES** (at least 5)
       - Format: "As a [user], I want [feature] so that [benefit]"
       - Include acceptance criteria for each
    
    4. 🎨 **USER EXPERIENCE EXPECTATIONS**
       - Key user flows
       - UI/UX priorities
       - Accessibility requirements
    
    5. 📊 **SUCCESS METRICS**
       - How will we measure success?
       - Key performance indicators
    
    6. 🚨 **CONSTRAINTS & RISKS**
       - Technical constraints
       - Budget/timeline considerations
       - Potential risks
    
    7. ❓ **OPEN QUESTIONS**
       - What needs clarification from the user?
       - Assumptions we're making
    
    Be specific, practical, and developer-friendly in your analysis.
    """
    
    try:
        response = gemini_model.generate_content(
            analyst_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.5,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
🎯 PRODUCT ANALYST REPORT
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Product Analyst AI

{response.text}

{'='*80}
✅ Analysis Complete - Ready for Architecture Team
{'='*80}
"""
        
        # Update project state
        project_state["requirements"] = response.text
        project_state["current_project"] = user_request
        
        return result
        
    except Exception as e:
        return f"❌ Product Analyst Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 2: RESEARCH ENGINEER
# =============================================================================

@mcp.tool()
def research_engineer(topic: str, focus_areas: List[str] = None) -> str:
    """
    🔍 Research Engineer - Searches the web for best practices, technologies, and solutions.
    
    This agent:
    - Researches current best practices
    - Finds relevant libraries and frameworks
    - Discovers similar projects and case studies
    - Identifies potential technical challenges and solutions
    
    Args:
        topic: What to research (e.g., "real-time chat applications")
        focus_areas: Specific aspects to focus on (e.g., ["scalability", "security"])
    
    Returns:
        Comprehensive research report with recommendations
    """
    if not GEMINI_AVAILABLE:
        return "❌ Research Engineer requires Gemini AI"
    
    # Perform multiple targeted searches
    search_queries = [
        f"{topic} best practices 2024 2025",
        f"{topic} architecture patterns",
        f"{topic} technology stack recommendations"
    ]
    
    if focus_areas:
        for area in focus_areas[:2]:  # Limit to 2 additional searches
            search_queries.append(f"{topic} {area} solutions")
    
    all_results = []
    for query in search_queries[:4]:  # Max 4 searches
        try:
            response = tavily_client.search(query, max_results=5)
            all_results.extend(response.get("results", []))
        except Exception as e:
            print(f"Search error for '{query}': {str(e)}")
    
    # Synthesize research findings with Gemini
    research_prompt = f"""
    You are an expert Research Engineer analyzing technical resources for: {topic}
    
    FOCUS AREAS: {', '.join(focus_areas) if focus_areas else 'General best practices'}
    
    RESEARCH DATA:
    {json.dumps(all_results, indent=2, default=str)[:12000]}
    
    Create a comprehensive research report:
    
    1. 🎯 **EXECUTIVE SUMMARY**
       - Key findings (3-5 bullet points)
       - Top recommendations
    
    2. 🛠️ **RECOMMENDED TECHNOLOGY STACK**
       - Frontend technologies and why
       - Backend technologies and why
       - Database recommendations
       - Key libraries/frameworks
       - DevOps tools
    
    3. 🏗️ **ARCHITECTURAL PATTERNS**
       - Recommended architecture style
       - Scalability considerations
       - Performance best practices
    
    4. 🔒 **SECURITY CONSIDERATIONS**
       - Common vulnerabilities to avoid
       - Security best practices
       - Authentication/authorization approaches
    
    5. 📚 **RELEVANT RESOURCES**
       - Top 3-5 resources from research
       - Why each is valuable
    
    6. ⚠️ **POTENTIAL CHALLENGES**
       - Common pitfalls
       - How to avoid them
    
    7. 💡 **INNOVATION OPPORTUNITIES**
       - Cutting-edge approaches worth considering
       - Emerging technologies relevant to this project
    
    Be specific with technology versions and practical implementation advice.
    """
    
    try:
        response = gemini_model.generate_content(
            research_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
🔍 RESEARCH ENGINEER REPORT
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Research Engineer AI
🔎 Searches Performed: {len(search_queries)}
📊 Sources Analyzed: {len(all_results)}

{response.text}

{'='*80}
✅ Research Complete - Ready for Architecture Design
{'='*80}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Research Engineer Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 3: SOFTWARE ARCHITECT
# =============================================================================

@mcp.tool()
def software_architect(requirements: str = None, research_findings: str = None) -> str:
    """
    🏗️ Software Architect - Designs system architecture and technical specifications.
    
    This agent:
    - Creates system architecture diagrams (described textually)
    - Defines data models and schemas
    - Plans API endpoints and interfaces
    - Specifies technology stack
    - Creates technical documentation
    
    Args:
        requirements: Product requirements (uses project state if not provided)
        research_findings: Research report (optional context)
    
    Returns:
        Detailed architecture design document
    """
    if not GEMINI_AVAILABLE:
        return "❌ Software Architect requires Gemini AI"
    
    # Use project state if not provided
    if not requirements:
        requirements = project_state.get("requirements", "No requirements available")
    
    architect_prompt = f"""
    You are an expert Software Architect designing a robust, scalable system.
    
    REQUIREMENTS:
    {requirements}
    
    RESEARCH CONTEXT:
    {research_findings if research_findings else "Use your expertise for technology choices"}
    
    Create a comprehensive architecture design:
    
    1. 🎯 **ARCHITECTURE OVERVIEW**
       - Architecture style (monolithic, microservices, serverless, etc.)
       - High-level component diagram (describe in text)
       - Data flow overview
       - Justification for architectural choices
    
    2. 🛠️ **TECHNOLOGY STACK SPECIFICATION**
       Frontend:
       - Framework/library (with version)
       - State management
       - UI component library
       - Build tools
       
       Backend:
       - Language and framework (with versions)
       - API style (REST, GraphQL, etc.)
       - Authentication method
       - Key libraries
       
       Database:
       - Type (SQL/NoSQL)
       - Specific database (PostgreSQL, MongoDB, etc.)
       - Caching strategy (Redis, etc.)
       
       Infrastructure:
       - Hosting platform
       - CI/CD tools
       - Monitoring/logging
    
    3. 📊 **DATA MODELS**
       - Define all major entities
       - Relationships between entities
       - Key fields for each entity
       - Indexes and constraints
    
    4. 🔌 **API DESIGN**
       - List all major endpoints
       - Request/response formats
       - Authentication/authorization flow
       - Rate limiting strategy
    
    5. 📁 **PROJECT STRUCTURE**
       - Directory/file organization
       - Module breakdown
       - Configuration management
    
    6. 🔒 **SECURITY ARCHITECTURE**
       - Authentication/authorization strategy
       - Data encryption approach
       - API security measures
       - OWASP top 10 mitigations
    
    7. 📈 **SCALABILITY PLAN**
       - Horizontal vs vertical scaling
       - Caching strategy
       - Load balancing approach
       - Database optimization
    
    8. 🔧 **DEVELOPMENT ENVIRONMENT**
       - Required tools and versions
       - Environment variables
       - Development setup steps
    
    Be extremely specific and implementation-ready.
    """
    
    try:
        response = gemini_model.generate_content(
            architect_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
🏗️ SOFTWARE ARCHITECT DESIGN DOCUMENT
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Software Architect AI

{response.text}

{'='*80}
✅ Architecture Complete - Ready for Implementation Planning
{'='*80}
"""
        
        # Update project state
        project_state["architecture"] = response.text
        
        return result
        
    except Exception as e:
        return f"❌ Software Architect Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 4: TECHNICAL LEAD
# =============================================================================

@mcp.tool()
def technical_lead(architecture: str = None) -> str:
    """
    📋 Technical Lead - Creates detailed implementation plan and task breakdown.
    
    This agent:
    - Breaks down architecture into implementable tasks
    - Defines development phases and milestones
    - Estimates effort for each task
    - Creates sprint planning
    - Identifies dependencies
    
    Args:
        architecture: Architecture document (uses project state if not provided)
    
    Returns:
        Detailed implementation plan with task breakdown
    """
    if not GEMINI_AVAILABLE:
        return "❌ Technical Lead requires Gemini AI"
    
    # Use project state if not provided
    if not architecture:
        architecture = project_state.get("architecture", "No architecture available")
    
    lead_prompt = f"""
    You are an expert Technical Lead creating an implementation plan.
    
    ARCHITECTURE:
    {architecture}
    
    Create a detailed implementation plan:
    
    1. 🎯 **DEVELOPMENT PHASES**
       Phase 1: Project Setup & Core Infrastructure
       Phase 2: Backend Development
       Phase 3: Frontend Development
       Phase 4: Integration & Testing
       Phase 5: Deployment & Launch
       
       For each phase, provide:
       - Duration estimate
       - Key deliverables
       - Success criteria
    
    2. 📋 **DETAILED TASK BREAKDOWN**
       For each phase, create specific tasks with:
       - Task ID (e.g., TASK-001)
       - Task name and description
       - Estimated hours/days
       - Priority (Critical, High, Medium, Low)
       - Dependencies (other task IDs)
       - Required skills
    
    3. 🗓️ **SPRINT PLANNING**
       - Organize tasks into 1-2 week sprints
       - Sprint goals
       - Task assignments per sprint
    
    4. 🔗 **DEPENDENCY MAP**
       - Critical path tasks
       - Parallel workstreams
       - Bottlenecks to watch
    
    5. 🎯 **MILESTONES & CHECKPOINTS**
       - Major milestones with dates
       - Demo/review points
       - Quality gates
    
    6. 📊 **RESOURCE ALLOCATION**
       - Recommended team composition
       - Skill requirements per phase
       - Third-party services needed
    
    7. ⚠️ **RISK MANAGEMENT**
       - Technical risks and mitigation
       - Schedule risks
       - Contingency plans
    
    8. 📝 **CODING STANDARDS & CONVENTIONS**
       - Naming conventions
       - Code structure guidelines
       - Documentation requirements
       - Git workflow
    
    Be extremely detailed and actionable. Each task should be clear enough for a developer to start immediately.
    """
    
    try:
        response = gemini_model.generate_content(
            lead_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
📋 TECHNICAL LEAD IMPLEMENTATION PLAN
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Technical Lead AI

{response.text}

{'='*80}
✅ Implementation Plan Complete - Ready for Development
{'='*80}
"""
        
        # Update project state
        project_state["implementation_plan"] = response.text
        
        return result
        
    except Exception as e:
        return f"❌ Technical Lead Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 5: SENIOR DEVELOPER
# =============================================================================

@mcp.tool()
def senior_developer(module_name: str, specifications: str, language: str = "python") -> str:
    """
    💻 Senior Developer - Writes production-ready code for specific modules.
    
    This agent:
    - Implements features according to specifications
    - Writes clean, maintainable code
    - Includes error handling and logging
    - Adds inline documentation
    - Follows best practices
    
    Args:
        module_name: Name of the module to implement
        specifications: Detailed specifications for this module
        language: Programming language (python, javascript, typescript, etc.)
    
    Returns:
        Production-ready code with documentation
    """
    if not GEMINI_AVAILABLE:
        return "❌ Senior Developer requires Gemini AI"
    
    developer_prompt = f"""
    You are an expert Senior Developer implementing a production-ready module.
    
    MODULE: {module_name}
    LANGUAGE: {language}
    
    SPECIFICATIONS:
    {specifications}
    
    PROJECT CONTEXT:
    Architecture: {project_state.get('architecture', 'See specifications')[:1000]}
    
    Write production-ready code with:
    
    1. 📝 **MODULE DOCUMENTATION**
       - Purpose and responsibilities
       - Dependencies
       - Usage examples
       - API documentation
    
    2. 💻 **IMPLEMENTATION**
       - Clean, readable code
       - Proper error handling
       - Input validation
       - Logging where appropriate
       - Type hints/annotations
       - Comments for complex logic
    
    3. ✅ **BEST PRACTICES**
       - Follow language-specific conventions
       - DRY principle
       - SOLID principles
       - Security best practices
       - Performance optimization
    
    4. 🧪 **TESTING CONSIDERATIONS**
       - Unit test examples (2-3 key tests)
       - Edge cases to consider
       - Mocking requirements
    
    5. 📋 **CONFIGURATION**
       - Environment variables needed
       - Configuration options
       - Default values
    
    6. 🔍 **CODE REVIEW NOTES**
       - Implementation decisions explained
       - Potential improvements for future
       - Known limitations
    
    Provide complete, runnable code with all necessary imports and setup.
    """
    
    try:
        response = gemini_model.generate_content(
            developer_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
💻 SENIOR DEVELOPER - MODULE IMPLEMENTATION
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Senior Developer AI
📦 Module: {module_name}
🔤 Language: {language}

{response.text}

{'='*80}
✅ Module Implementation Complete - Ready for Review & Testing
{'='*80}
"""
        
        # Store in project state
        if "code_modules" not in project_state:
            project_state["code_modules"] = {}
        project_state["code_modules"][module_name] = response.text
        
        return result
        
    except Exception as e:
        return f"❌ Senior Developer Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 6: QA ENGINEER
# =============================================================================

@mcp.tool()
def qa_engineer(module_name: str, code: str = None, test_type: str = "comprehensive") -> str:
    """
    🧪 QA Engineer - Creates comprehensive test suites and quality assurance plans.
    
    This agent:
    - Writes unit tests
    - Creates integration tests
    - Designs test scenarios
    - Identifies edge cases
    - Creates test automation scripts
    
    Args:
        module_name: Name of module to test
        code: The code to test (uses project state if not provided)
        test_type: Type of testing (unit, integration, e2e, comprehensive)
    
    Returns:
        Complete test suite with multiple test scenarios
    """
    if not GEMINI_AVAILABLE:
        return "❌ QA Engineer requires Gemini AI"
    
    # Try to get code from project state if not provided
    if not code:
        code = project_state.get("code_modules", {}).get(module_name, "No code available")
    
    qa_prompt = f"""
    You are an expert QA Engineer creating comprehensive tests for: {module_name}
    
    TEST TYPE: {test_type}
    
    CODE TO TEST:
    {code[:6000]}
    
    PROJECT CONTEXT:
    {project_state.get('architecture', 'No architecture available')[:1000]}
    
    Create a comprehensive testing strategy:
    
    1. 📋 **TEST PLAN OVERVIEW**
       - Testing objectives
       - Scope and coverage
       - Testing approach
       - Success criteria
    
    2. 🧪 **UNIT TESTS**
       - At least 10 unit test cases
       - Test function/method names
       - Input/output specifications
       - Mock requirements
       - Edge cases
       - Complete test code
    
    3. 🔗 **INTEGRATION TESTS**
       - Integration scenarios (at least 5)
       - External dependencies to test
       - Test data requirements
       - Complete test code
    
    4. 🎭 **END-TO-END TESTS**
       - User flow scenarios
       - Expected behaviors
       - Test automation approach
       - Sample E2E test code
    
    5. ⚠️ **ERROR HANDLING TESTS**
       - Invalid input scenarios
       - Exception handling tests
       - Error recovery tests
    
    6. 🔒 **SECURITY TESTS**
       - Authentication/authorization tests
       - Input validation tests
       - SQL injection / XSS prevention tests
    
    7. 📊 **PERFORMANCE TESTS**
       - Load testing scenarios
       - Performance benchmarks
       - Stress test cases
    
    8. ✅ **TEST DATA**
       - Sample valid data
       - Sample invalid data
       - Edge case data
       - Mock data generators
    
    9. 🤖 **TEST AUTOMATION**
       - CI/CD integration approach
       - Test runner configuration
       - Coverage requirements (aim for 80%+)
    
    10. 📝 **QUALITY METRICS**
        - Coverage targets
        - Performance benchmarks
        - Quality gates
    
    Provide complete, runnable test code using appropriate testing framework.
    """
    
    try:
        response = gemini_model.generate_content(
            qa_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
🧪 QA ENGINEER - TEST SUITE
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: QA Engineer AI
📦 Module: {module_name}
🎯 Test Type: {test_type}

{response.text}

{'='*80}
✅ Test Suite Complete - Ready for Execution
{'='*80}
"""
        
        return result
        
    except Exception as e:
        return f"❌ QA Engineer Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 7: DEVOPS ENGINEER
# =============================================================================

@mcp.tool()
def devops_engineer(environment: str = "production", deployment_type: str = "cloud") -> str:
    """
    🚀 DevOps Engineer - Creates deployment configurations and CI/CD pipelines.
    
    This agent:
    - Creates Docker configurations
    - Designs CI/CD pipelines
    - Configures infrastructure as code
    - Sets up monitoring and logging
    - Creates deployment documentation
    
    Args:
        environment: Target environment (development, staging, production)
        deployment_type: Type of deployment (cloud, on-premise, serverless)
    
    Returns:
        Complete deployment and infrastructure configuration
    """
    if not GEMINI_AVAILABLE:
        return "❌ DevOps Engineer requires Gemini AI"
    
    devops_prompt = f"""
    You are an expert DevOps Engineer setting up deployment infrastructure.
    
    ENVIRONMENT: {environment}
    DEPLOYMENT TYPE: {deployment_type}
    
    PROJECT CONTEXT:
    Architecture: {project_state.get('architecture', 'No architecture available')[:2000]}
    
    Create a comprehensive deployment strategy:
    
    1. 🐳 **CONTAINERIZATION**
       - Complete Dockerfile(s)
       - Docker Compose configuration
       - Multi-stage build optimization
       - Health checks
       - Environment variable management
    
    2. 🔄 **CI/CD PIPELINE**
       - GitHub Actions / GitLab CI / Jenkins configuration
       - Build pipeline steps
       - Test automation integration
       - Deployment stages (dev → staging → production)
       - Rollback procedures
       - Complete pipeline YAML
    
    3. ☁️ **INFRASTRUCTURE AS CODE**
       - Cloud provider choice and justification
       - Terraform/CloudFormation/Pulumi scripts
       - Resource definitions (compute, storage, network)
       - Scaling configurations
       - Cost optimization strategies
    
    4. 🔒 **SECURITY CONFIGURATION**
       - Secret management (AWS Secrets Manager, Vault, etc.)
       - Network security groups
       - SSL/TLS certificates
       - Access control (IAM roles/policies)
       - Security scanning in pipeline
    
    5. 📊 **MONITORING & LOGGING**
       - Monitoring stack (Prometheus, Grafana, Datadog, etc.)
       - Log aggregation (ELK, CloudWatch, etc.)
       - Alert configurations
       - Dashboard templates
       - APM integration
    
    6. 🗄️ **DATABASE DEPLOYMENT**
       - Database provisioning
       - Migration strategy
       - Backup configuration
       - Disaster recovery plan
       - Connection pooling
    
    7. 🌐 **NETWORKING & LOAD BALANCING**
       - Load balancer configuration
       - CDN setup
       - DNS management
       - SSL termination
       - Rate limiting
    
    8. 📈 **SCALING STRATEGY**
       - Horizontal scaling rules
       - Auto-scaling configuration
       - Resource limits
       - Cost thresholds
    
    9. 🔧 **CONFIGURATION MANAGEMENT**
       - Environment-specific configs
       - Feature flags
       - Configuration validation
       - Secret rotation
    
    10. 📝 **DEPLOYMENT DOCUMENTATION**
        - Deployment checklist
        - Rollback procedures
        - Troubleshooting guide
        - Runbook for common operations
    
    Provide complete, copy-paste ready configuration files.
    """
    
    try:
        response = gemini_model.generate_content(
            devops_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
🚀 DEVOPS ENGINEER - DEPLOYMENT CONFIGURATION
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: DevOps Engineer AI
🌍 Environment: {environment}
☁️ Deployment Type: {deployment_type}

{response.text}

{'='*80}
✅ Deployment Configuration Complete - Ready for Deployment
{'='*80}
"""
        
        # Update project state
        project_state["deployment_plan"] = response.text
        
        return result
        
    except Exception as e:
        return f"❌ DevOps Engineer Error: {str(e)}"

# =============================================================================
# TEAM MEMBER 8: DOCUMENTATION SPECIALIST
# =============================================================================

@mcp.tool()
def documentation_specialist(doc_type: str = "complete") -> str:
    """
    📚 Documentation Specialist - Creates comprehensive project documentation.
    
    This agent:
    - Writes README files
    - Creates API documentation
    - Writes user guides
    - Creates developer onboarding docs
    - Generates architecture diagrams descriptions
    
    Args:
        doc_type: Type of documentation (readme, api, user_guide, developer_guide, complete)
    
    Returns:
        Professional documentation in Markdown format
    """
    if not GEMINI_AVAILABLE:
        return "❌ Documentation Specialist requires Gemini AI"
    
    # Gather all context from project state
    context = f"""
    PROJECT: {project_state.get('current_project', 'No project info')}
    
    REQUIREMENTS:
    {project_state.get('requirements', 'No requirements')[:2000]}
    
    ARCHITECTURE:
    {project_state.get('architecture', 'No architecture')[:2000]}
    
    IMPLEMENTATION PLAN:
    {project_state.get('implementation_plan', 'No implementation plan')[:1000]}
    """
    
    doc_prompt = f"""
    You are an expert Technical Documentation Specialist creating {doc_type} documentation.
    
    PROJECT CONTEXT:
    {context}
    
    Create professional, comprehensive documentation:
    
    1. 📘 **README.md** (Main Project README)
       - Project title and description
       - Features and capabilities
       - Screenshots/demo links (placeholders)
       - Quick start guide
       - Installation instructions
       - Usage examples
       - Configuration guide
       - Contributing guidelines
       - License information
       - Contact/support information
    
    2. 📖 **API_DOCUMENTATION.md**
       - API overview
       - Authentication
       - All endpoints with:
         * HTTP method and path
         * Description
         * Request parameters
         * Request body example
         * Response format
         * Status codes
         * Error handling
       - Rate limiting
       - Versioning
       - Examples with curl/code
    
    3. 👥 **USER_GUIDE.md**
       - Getting started
       - Step-by-step tutorials
       - Feature explanations
       - Common use cases
       - Troubleshooting FAQ
       - Tips and best practices
    
    4. 👨‍💻 **DEVELOPER_GUIDE.md**
       - Development environment setup
       - Project structure explanation
       - Architecture overview
       - Code organization
       - Coding standards
       - Testing guide
       - Debugging tips
       - Contributing workflow
       - Release process
    
    5. 🏗️ **ARCHITECTURE.md**
       - System overview
       - Component diagram (textual description)
       - Data flow
       - Technology stack details
       - Design decisions and rationale
       - Scalability considerations
       - Security architecture
    
    6. 🚀 **DEPLOYMENT.md**
       - Prerequisites
       - Environment setup
       - Configuration guide
       - Deployment steps
       - Monitoring setup
       - Rollback procedures
       - Production checklist
    
    7. 📊 **CHANGELOG.md**
       - Version history format
       - Template for future updates
    
    Use proper Markdown formatting with headers, code blocks, tables, and lists.
    Make it professional and easy to navigate.
    """
    
    try:
        response = gemini_model.generate_content(
            doc_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        result = f"""
{'='*80}
📚 DOCUMENTATION SPECIALIST - PROJECT DOCUMENTATION
{'='*80}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Agent: Documentation Specialist AI
📋 Documentation Type: {doc_type}

{response.text}

{'='*80}
✅ Documentation Complete - Ready for Review
{'='*80}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Documentation Specialist Error: {str(e)}"

# =============================================================================
# ORCHESTRATOR - THE TEAM COORDINATOR
# =============================================================================

@mcp.tool()
def orchestrator(user_request: str, auto_execute: bool = True, execution_mode: str = "full") -> str:
    """
    🎯 ORCHESTRATOR - Intelligent team coordinator that manages the entire software development process.
    
    This is the main entry point for building applications. The orchestrator:
    - Analyzes your request
    - Determines which team members to involve
    - Executes tasks in the optimal order
    - Manages dependencies between team members
    - Combines all outputs into a cohesive project
    
    Args:
        user_request: Your application idea (e.g., "Build a real-time chat application with React and Node.js")
        auto_execute: Whether to automatically execute the plan (default: True)
        execution_mode: 
            - "full" = Complete end-to-end development (all 8 team members)
            - "planning" = Analysis, research, and architecture only (first 3 team members)
            - "implementation" = Add implementation and testing (5 team members)
            - "deployment" = Full project with deployment ready (7 team members)
            - "custom" = Let orchestrator decide based on request
    
    Returns:
        Complete project deliverables from all team members
    """
    if not GEMINI_AVAILABLE:
        return "❌ Orchestrator requires Gemini AI for intelligent coordination"
    
    # Reset project state for new project
    project_state["current_project"] = user_request
    project_state["requirements"] = None
    project_state["architecture"] = None
    project_state["implementation_plan"] = None
    project_state["code_modules"] = {}
    project_state["deployment_plan"] = None
    
    # Step 1: Analyze the request and create execution plan
    analysis_prompt = f"""
    You are the Orchestrator AI coordinating a team of 8 software engineering specialists.
    
    USER REQUEST: "{user_request}"
    
    EXECUTION MODE: {execution_mode}
    
    AVAILABLE TEAM MEMBERS:
    1. 🎯 product_analyst - Analyzes requirements and creates specifications
    2. 🔍 research_engineer - Researches technologies and best practices
    3. 🏗️ software_architect - Designs system architecture
    4. 📋 technical_lead - Creates implementation plan and task breakdown
    5. 💻 senior_developer - Implements code modules
    6. 🧪 qa_engineer - Creates test suites
    7. 🚀 devops_engineer - Creates deployment configurations
    8. 📚 documentation_specialist - Creates comprehensive documentation
    
    EXECUTION MODE GUIDELINES:
    - "full": Use ALL 8 team members for complete project delivery
    - "planning": Use members 1-3 (analysis, research, architecture)
    - "implementation": Use members 1-5 (add implementation)
    - "deployment": Use members 1-7 (add DevOps)
    - "custom": Intelligently choose based on request complexity
    
    Analyze the request and respond with JSON:
    {{
        "project_name": "Suggested project name",
        "complexity": "simple|moderate|complex|enterprise",
        "analysis": "Brief analysis of what needs to be built",
        "recommended_mode": "Recommended execution mode if custom",
        "team_workflow": [
            {{
                "step": 1,
                "agent": "product_analyst",
                "parameters": {{"user_request": "...", "additional_context": "..."}},
                "reason": "Why this agent is needed",
                "estimated_time": "Time estimate"
            }},
            {{
                "step": 2,
                "agent": "research_engineer",
                "parameters": {{"topic": "...", "focus_areas": ["..."]}},
                "reason": "Why this agent is needed",
                "estimated_time": "Time estimate",
                "depends_on": [1]
            }}
        ],
        "key_modules": ["List of main modules to implement if senior_developer is involved"],
        "success_criteria": ["How we'll know the project is complete"],
        "estimated_total_time": "Overall project timeline"
    }}
    
    Be smart about:
    - What needs to be researched
    - Which modules need custom implementation
    - Dependencies between team members
    - Optimal execution order
    """
    
    try:
        print("\n🤔 Orchestrator analyzing request...")
        analysis_response = gemini_model.generate_content(
            analysis_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=4096,
            )
        )
        
        # Extract JSON from response
        analysis_text = analysis_response.text
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            return f"❌ Could not parse orchestrator analysis: {analysis_text}"
            
    except Exception as e:
        return f"❌ Orchestrator Analysis Error: {str(e)}"
    
    # Step 2: Show the execution plan
    plan_summary = f"""
{'='*80}
🎯 ORCHESTRATOR - AI SOFTWARE ENGINEERING TEAM
{'='*80}
📅 Project Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🏢 Project: {plan.get('project_name', 'Unnamed Project')}
📊 Complexity: {plan.get('complexity', 'Unknown').upper()}
⏱️ Estimated Time: {plan.get('estimated_total_time', 'Unknown')}

📋 PROJECT ANALYSIS:
{plan.get('analysis', 'No analysis provided')}

✅ SUCCESS CRITERIA:
{chr(10).join([f"  • {criteria}" for criteria in plan.get('success_criteria', [])])}

🔧 TEAM WORKFLOW ({len(plan.get('team_workflow', []))} steps):
"""
    
    for step_info in plan.get('team_workflow', []):
        step_num = step_info.get('step', 0)
        agent = step_info.get('agent', 'unknown')
        reason = step_info.get('reason', 'No reason provided')
        time = step_info.get('estimated_time', 'Unknown')
        depends = step_info.get('depends_on', [])
        
        plan_summary += f"\n  Step {step_num}: {agent.upper().replace('_', ' ')}"
        plan_summary += f"\n    ⏱️  Time: {time}"
        plan_summary += f"\n    💡 Reason: {reason}"
        if depends:
            plan_summary += f"\n    🔗 Depends on steps: {', '.join(map(str, depends))}"
        plan_summary += "\n"
    
    if plan.get('key_modules'):
        plan_summary += f"\n📦 KEY MODULES TO IMPLEMENT:\n"
        for module in plan['key_modules']:
            plan_summary += f"  • {module}\n"
    
    if not auto_execute:
        plan_summary += f"\n\n💡 Set auto_execute=True to execute this plan automatically."
        return plan_summary
    
    # Step 3: Execute the workflow
    plan_summary += f"\n\n{'='*80}\n🚀 EXECUTING TEAM WORKFLOW\n{'='*80}\n"
    
    results = {}
    workflow_outputs = []
    
    for step_info in plan.get('team_workflow', []):
        agent_name = step_info.get('agent', '')
        parameters = step_info.get('parameters', {})
        step_num = step_info.get('step', 0)
        
        print(f"\n▶️  Step {step_num}: Executing {agent_name}...")
        plan_summary += f"\n{'─'*80}\n▶️  STEP {step_num}: {agent_name.upper().replace('_', ' ')}\n{'─'*80}\n"
        
        try:
            # Execute the appropriate agent
            if agent_name == "product_analyst":
                result = product_analyst(
                    parameters.get('user_request', user_request),
                    parameters.get('additional_context', '')
                )
            elif agent_name == "research_engineer":
                result = research_engineer(
                    parameters.get('topic', user_request),
                    parameters.get('focus_areas', [])
                )
            elif agent_name == "software_architect":
                result = software_architect(
                    parameters.get('requirements'),
                    parameters.get('research_findings')
                )
            elif agent_name == "technical_lead":
                result = technical_lead(parameters.get('architecture'))
            elif agent_name == "senior_developer":
                # For senior developer, we might need to implement multiple modules
                module_name = parameters.get('module_name', 'main_module')
                result = senior_developer(
                    module_name,
                    parameters.get('specifications', 'Implement according to architecture'),
                    parameters.get('language', 'python')
                )
            elif agent_name == "qa_engineer":
                result = qa_engineer(
                    parameters.get('module_name', 'main_module'),
                    parameters.get('code'),
                    parameters.get('test_type', 'comprehensive')
                )
            elif agent_name == "devops_engineer":
                result = devops_engineer(
                    parameters.get('environment', 'production'),
                    parameters.get('deployment_type', 'cloud')
                )
            elif agent_name == "documentation_specialist":
                result = documentation_specialist(parameters.get('doc_type', 'complete'))
            else:
                result = f"❌ Unknown agent: {agent_name}"
            
            results[agent_name] = result
            workflow_outputs.append(result)
            
            # Show abbreviated result in summary
            result_preview = result[:800] + "..." if len(result) > 800 else result
            plan_summary += f"{result_preview}\n"
            
        except Exception as e:
            error_msg = f"❌ Error executing {agent_name}: {str(e)}"
            print(error_msg)
            plan_summary += f"{error_msg}\n"
            results[agent_name] = error_msg
    
    # Step 4: Generate project summary
    summary_prompt = f"""
    You are the Orchestrator AI providing a final project summary.
    
    ORIGINAL REQUEST: {user_request}
    
    PROJECT NAME: {plan.get('project_name', 'Unnamed Project')}
    
    TEAM OUTPUTS SUMMARY:
    {json.dumps({k: str(v)[:500] + "..." for k, v in results.items()}, indent=2)}
    
    Create a comprehensive project delivery summary:
    
    1. 🎯 **PROJECT OVERVIEW**
       - What was built
       - Key features delivered
       - Technology stack used
    
    2. ✅ **DELIVERABLES CHECKLIST**
       - Mark what was completed by each team member
       - Highlight key artifacts created
    
    3. 📊 **PROJECT STATUS**
       - Overall completion status
       - Quality assessment
       - Readiness for next phase
    
    4. 🚀 **NEXT STEPS**
       - What the user should do next
       - How to use the deliverables
       - Recommended actions
    
    5. 💡 **KEY INSIGHTS & RECOMMENDATIONS**
       - Important architectural decisions made
       - Best practices applied
       - Things to consider for future development
    
    6. 📁 **ARTIFACT LOCATIONS**
       - Where to find each deliverable in the conversation
       - How to use each artifact
    
    Be concise but comprehensive. This is the executive summary.
    """
    
    try:
        print("\n📊 Generating final project summary...")
        summary_response = gemini_model.generate_content(
            summary_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=4096,
            )
        )
        
        plan_summary += f"\n\n{'='*80}\n🎯 PROJECT DELIVERY SUMMARY\n{'='*80}\n\n{summary_response.text}\n"
        
    except Exception as e:
        plan_summary += f"\n\n❌ Error generating summary: {str(e)}"
    
    # Final output
    plan_summary += f"\n\n{'='*80}\n✅ PROJECT COMPLETE\n{'='*80}\n"
    plan_summary += f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    plan_summary += f"👥 Team Members Involved: {len(results)}\n"
    plan_summary += f"📦 Artifacts Generated: {len(workflow_outputs)}\n"
    plan_summary += f"\n💡 All detailed outputs are available above. Scroll up to see complete deliverables from each team member.\n"
    
    return plan_summary

# =============================================================================
# UTILITY TOOLS
# =============================================================================

@mcp.tool()
def team_status() -> Dict:
    """
    Get current status of the AI software engineering team and ongoing project.
    
    Returns:
        Status of all team members and current project state
    """
    return {
        "server_version": "2.0.0 - AI Software Engineering Team",
        "team_size": 8,
        "services": {
            "tavily_search": "✅ Connected" if TAVILY_API_KEY else "❌ Not configured",
            "gemini_ai": "✅ Connected" if GEMINI_AVAILABLE else f"❌ Not available",
            "orchestrator": "✅ Available" if GEMINI_AVAILABLE else "❌ Requires Gemini"
        },
        "team_members": [
            "🎯 product_analyst - Requirements & Product Specs",
            "🔍 research_engineer - Technology Research",
            "🏗️ software_architect - System Architecture",
            "📋 technical_lead - Implementation Planning",
            "💻 senior_developer - Code Implementation",
            "🧪 qa_engineer - Testing & Quality Assurance",
            "🚀 devops_engineer - Deployment & Infrastructure",
            "📚 documentation_specialist - Documentation"
        ],
        "current_project": {
            "name": project_state.get("current_project", "No active project"),
            "has_requirements": project_state.get("requirements") is not None,
            "has_architecture": project_state.get("architecture") is not None,
            "has_implementation_plan": project_state.get("implementation_plan") is not None,
            "code_modules_count": len(project_state.get("code_modules", {})),
            "has_deployment_plan": project_state.get("deployment_plan") is not None
        },
        "usage_tip": "Call orchestrator(your_request) to start building an application with the full team!"
    }

@mcp.tool()
def export_project_files(output_directory: str = "generated_project", include_docs: bool = True) -> str:
    """
    Export all project artifacts to a structured folder with code files and documentation.
    
    Args:
        output_directory: Name of the output directory (default: "generated_project")
        include_docs: Whether to include documentation files (default: True)
    
    Returns:
        Status message with export details and folder structure
    """
    if not project_state.get("current_project"):
        return "❌ No active project to export. Run orchestrator() first to generate a project."
    
    try:
        # Create base directory
        base_path = Path(output_directory)
        if base_path.exists():
            # Create backup of existing directory
            backup_path = Path(f"{output_directory}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.move(str(base_path), str(backup_path))
        
        base_path.mkdir(exist_ok=True)
        
        # Create project structure
        folders_created = []
        files_created = []
        
        # 1. Create main project folders
        (base_path / "src").mkdir(exist_ok=True)
        (base_path / "tests").mkdir(exist_ok=True)
        (base_path / "docs").mkdir(exist_ok=True)
        (base_path / "config").mkdir(exist_ok=True)
        (base_path / "scripts").mkdir(exist_ok=True)
        folders_created.extend(["src", "tests", "docs", "config", "scripts"])
        
        # 2. Export code modules
        code_modules = project_state.get("code_modules", {})
        for module_name, module_content in code_modules.items():
            # Determine file extension based on content
            if "import React" in str(module_content) or "jsx" in module_name.lower():
                file_ext = ".jsx"
                folder = "src/components"
            elif "from flask" in str(module_content) or "app.py" in module_name:
                file_ext = ".py"
                folder = "src"
            elif "package.json" in module_name:
                file_ext = ".json"
                folder = ""
            elif "dockerfile" in module_name.lower():
                file_ext = ""
                folder = "config"
            elif "test" in module_name.lower():
                file_ext = ".py" if "python" in str(module_content).lower() else ".js"
                folder = "tests"
            else:
                file_ext = ".py"  # default
                folder = "src"
            
            # Create subfolder if needed
            if folder:
                (base_path / folder).mkdir(parents=True, exist_ok=True)
                file_path = base_path / folder / f"{module_name}{file_ext}"
            else:
                file_path = base_path / f"{module_name}{file_ext}"
            
            # Write module content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(module_content))
            files_created.append(str(file_path.relative_to(base_path)))
        
        # 3. Export requirements/architecture documents
        if project_state.get("requirements"):
            req_file = base_path / "docs" / "requirements.md"
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write(f"# Project Requirements\n\n{project_state['requirements']}")
            files_created.append("docs/requirements.md")
        
        if project_state.get("architecture"):
            arch_file = base_path / "docs" / "architecture.md"
            with open(arch_file, 'w', encoding='utf-8') as f:
                f.write(f"# System Architecture\n\n{project_state['architecture']}")
            files_created.append("docs/architecture.md")
        
        if project_state.get("implementation_plan"):
            plan_file = base_path / "docs" / "implementation_plan.md"
            with open(plan_file, 'w', encoding='utf-8') as f:
                f.write(f"# Implementation Plan\n\n{project_state['implementation_plan']}")
            files_created.append("docs/implementation_plan.md")
        
        if project_state.get("deployment_plan"):
            deploy_file = base_path / "docs" / "deployment.md"
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(f"# Deployment Guide\n\n{project_state['deployment_plan']}")
            files_created.append("docs/deployment.md")
        
        # 4. Create README.md
        readme_content = f"""# {project_state.get('current_project', 'Generated Project')}

## Project Overview
This project was generated by the AI Software Engineering Team.

## Project Structure
```
{output_directory}/
├── src/                 # Source code
├── tests/              # Test files
├── docs/               # Documentation
├── config/             # Configuration files
├── scripts/            # Build and deployment scripts
└── README.md           # This file
```

## Generated Files
{chr(10).join([f'- {file}' for file in files_created])}

## Getting Started
1. Review the documentation in the `docs/` folder
2. Check the implementation plan for development steps
3. Follow the deployment guide for production setup

## Team Members Involved
- 🎯 Product Analyst
- 🔍 Research Engineer
- 🏗️ Software Architect
- 📋 Technical Lead
- 💻 Senior Developer
- 🧪 QA Engineer
- 🚀 DevOps Engineer
- 📚 Documentation Specialist

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_file = base_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        # 5. Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.production

# Build outputs
dist/
build/
*.egg-info/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.temp
"""
        
        gitignore_file = base_path / ".gitignore"
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        files_created.append(".gitignore")
        
        # Generate summary
        result = f"""
{'='*80}
📁 PROJECT EXPORT COMPLETE
{'='*80}
📅 Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📂 Output Directory: {output_directory}
📊 Project: {project_state.get('current_project', 'Unknown')}

✅ EXPORT SUMMARY:
  • Folders Created: {len(folders_created)}
  • Files Exported: {len(files_created)}
  • Code Modules: {len(code_modules)}
  • Documentation Files: {len([f for f in files_created if f.startswith('docs/')])}

📁 FOLDER STRUCTURE:
{output_directory}/
├── src/                 # Source code ({len([f for f in files_created if f.startswith('src/')])} files)
├── tests/              # Test files ({len([f for f in files_created if f.startswith('tests/')])} files)
├── docs/               # Documentation ({len([f for f in files_created if f.startswith('docs/')])} files)
├── config/             # Configuration ({len([f for f in files_created if f.startswith('config/')])} files)
├── scripts/            # Scripts ({len([f for f in files_created if f.startswith('scripts/')])} files)
├── README.md           # Project overview
└── .gitignore          # Git ignore rules

📋 EXPORTED FILES:
{chr(10).join([f'  • {file}' for file in sorted(files_created)])}

🚀 NEXT STEPS:
1. Navigate to the '{output_directory}' folder
2. Review README.md for project overview
3. Check docs/ folder for detailed documentation
4. Follow implementation plan for development
5. Use deployment guide for production setup

💡 TIP: You can now work with these files in your preferred IDE!
{'='*80}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Export failed: {str(e)}"

@mcp.tool()
def reset_project() -> str:
    """
    Reset the current project state to start fresh.
    
    Returns:
        Confirmation message
    """
    project_state["current_project"] = None
    project_state["requirements"] = None
    project_state["architecture"] = None
    project_state["tech_stack"] = None
    project_state["implementation_plan"] = None
    project_state["code_modules"] = {}
    project_state["testing_results"] = None
    project_state["deployment_plan"] = None
    
    return "✅ Project state reset successfully. Ready for a new project!"

@mcp.tool()
def get_project_summary() -> str:
    """
    Get a quick summary of the current project state.
    
    Returns:
        Summary of project progress and available artifacts
    """
    if not project_state.get("current_project"):
        return "ℹ️ No active project. Start one with orchestrator(your_request)!"
    
    summary = f"""
🏗️ **CURRENT PROJECT SUMMARY**
{'='*60}

📋 Project: {project_state.get('current_project', 'Unknown')}

✅ Completed Phases:
  • Requirements Analysis: {'✓' if project_state.get('requirements') else '✗'}
  • System Architecture: {'✓' if project_state.get('architecture') else '✗'}
  • Implementation Plan: {'✓' if project_state.get('implementation_plan') else '✗'}
  • Code Modules: {len(project_state.get('code_modules', {}))} implemented
  • Deployment Plan: {'✓' if project_state.get('deployment_plan') else '✗'}

📦 Available Artifacts:
"""
    
    if project_state.get('code_modules'):
        summary += "\n  Implemented Modules:\n"
        for module_name in project_state['code_modules'].keys():
            summary += f"    • {module_name}\n"
    
    summary += "\n💡 Use individual team member tools to continue development!"
    
    return summary

# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 AI SOFTWARE ENGINEERING TEAM - MCP SERVER")
    print("="*80)
    print(f"\n📡 Server Status:")
    print(f"  • Port: {PORT}")
    print(f"  • Tavily Search: {'✅ Ready' if TAVILY_API_KEY else '❌ Not configured'}")
    print(f"  • Gemini AI: {'✅ Ready' if GEMINI_AVAILABLE else '❌ Not available'}")
    print(f"  • Orchestrator: {'✅ Ready' if GEMINI_AVAILABLE else '❌ Requires Gemini'}")
    
    print(f"\n👥 Team Members (8 specialists):")
    print(f"  1. 🎯 Product Analyst")
    print(f"  2. 🔍 Research Engineer")
    print(f"  3. 🏗️ Software Architect")
    print(f"  4. 📋 Technical Lead")
    print(f"  5. 💻 Senior Developer")
    print(f"  6. 🧪 QA Engineer")
    print(f"  7. 🚀 DevOps Engineer")
    print(f"  8. 📚 Documentation Specialist")
    
    print(f"\n💡 Quick Start:")
    print(f"  Call: orchestrator('Build a [your app idea]')")
    print(f"  Example: orchestrator('Build a task management app with React and Node.js')")
    
    print("\n" + "="*80 + "\n")
    
    mcp.run(transport="streamable-http")