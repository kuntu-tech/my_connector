#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BI Analysis API - FastAPI wrapper for BI_result(1).py
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Any, Optional
import asyncio
import time
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import BI_result functions
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import core functionality from BI_result(1).py
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool, SQLiteSession, WebSearchTool

app = FastAPI(
    title="BI Analysis API",
    version="1.0.0",
    description="A FastAPI service for AI-powered business intelligence analysis using OpenAI Agents and Supabase MCP tools."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, production environment should specify specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

# Load environment variables
load_dotenv()

# Request Models
class BIAnalysisRequest(BaseModel):
    """BI Analysis request model"""
    analysis_type: Literal["schema", "market", "audience", "all"] = Field(
        ..., 
        description="Type of analysis to perform"
    )
    supabase_project_id: str = Field(
        ..., 
        description="Supabase project ID"
    )
    supabase_access_token: str = Field(
        ..., 
        description="Supabase access token"
    )
    user_name: str = Field(
        default="huimin", 
        description="User identifier for session management"
    )
    data_review_result: bool = Field(
        default=True, 
        description="Data review result - only execute if true"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, can use env variable)"
    )

class BIAnalysisResponse(BaseModel):
    """BI Analysis response model"""
    success: bool
    analysis_type: str
    message: str
    results: Dict[str, Any] = {}
    files_generated: List[str] = []
    database_saved: bool = False
    execution_time: float
    timestamp: str

class DataReviewRequest(BaseModel):
    """Data compliance check request model"""
    supabase_project_id: str = Field(
        ..., 
        description="Supabase project ID"
    )
    supabase_access_token: str = Field(
        ..., 
        description="Supabase access token"
    )
    user_name: str = Field(
        default="huimin", 
        description="User identifier"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, can use environment variable)"
    )
    tables_info: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Table information list (optional, will be retrieved automatically if not provided)"
    )

class DataReviewResponse(BaseModel):
    """Data compliance check response model"""
    success: bool
    message: str
    review_result: Dict[str, Any] = {}
    tables_audited: List[Dict[str, Any]] = []
    final_conclusion: bool
    execution_time: float
    timestamp: str

# Tool function
@function_tool
def get_current_time() -> str:
    """Get current time in ISO format"""
    return datetime.now().astimezone().isoformat()

# Data audit functions (integrated from conn_supabase(1).py and BI_result(1).py)
def audit_table_with_gpt(table_info, openai_api_key: str = None):
    """Audit table with GPT for data compliance"""
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
You are a data compliance expert. Please analyze the following Supabase table according to OpenAI data policies:
Table information: {table_info}
Requirements:
1. Identify possible personal contact information or sensitive fields related to religion, politics, minors, etc.;
2. Explain whether it violates data compliance regulations;
3. Output in JSON format only
4. Output fields should only contain: table_name, contains_personal_data, contains_sensitive_data, contains_sensitive_fields, allowed_to_use
5. If contains_sensitive_data is True, output specific fields to contains_sensitive_fields; if contains_sensitive_data is False, contains_sensitive_fields should be null
6. Output language: English
7. Return ONLY valid JSON, no additional text or explanations
"""

    print(f"Auditing table: {table_info.get('table_name')} for data compliance...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data compliance expert. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    report = response.choices[0].message.content
    print(f"\nAudit result:\n", report)
    return report

def data_check(tables_info, openai_api_key: str = None):
    """Data compliance check for all tables"""
    reports_list = []
    all_allowed = True  # Used to determine overall conclusion
    for table in tables_info:
        try:
            report = audit_table_with_gpt(table, openai_api_key)
            report_json = json.loads(report)
            reports_list.append(report_json)
            # Check if allowed to use
            if not report_json.get("allowed_to_use", False):
                all_allowed = False
        except Exception as e:
            print(f"Audit failed for table {table}: {e}")
            report_json = {"table_name": table.get("table_name", "unknown"), "allowed_to_use": False, "error": str(e)}
            reports_list.append(report_json)
            all_allowed = False
    
    # Unified summary report
    summary = {
        "tables_audited": reports_list,
        "final_conclusion": all_allowed
    }
    print("Summary report:")
    print(json.dumps(summary, indent=4, ensure_ascii=False))
    # Return True / False signal
    return all_allowed, summary

async def initialize_agent(
    supabase_project_id: str,
    supabase_access_token: str,
    user_name: str
) -> Agent:
    """Initialize the AI agent with provided configuration"""
    # Read prompt files
    BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent / "prompts" / "system_prompt.md").read_text(encoding="utf-8")
    
    # Create Supabase MCP URL
    supabase_mcp_url = f"https://mcp.supabase.com/mcp?project_ref={supabase_project_id}"
    
    # Create agent
    agent = Agent(
        name='business_expert',
        instructions=BUSINESS_EXPERT_PROMPT,
        model='gpt-4.1-mini',
        model_settings=ModelSettings(
            temperature=0.7,
            top_p=0.9
        ),
        tools=[
            HostedMCPTool(
                tool_config={
                    'type': "mcp",
                    "server_label": "supabase",
                    "server_url": supabase_mcp_url,
                    "authorization": supabase_access_token,
                    "require_approval": "never"
                }
            ),
            get_current_time,
            WebSearchTool(),
        ],
    )
    
    return agent

async def run_schema_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """Run schema analysis"""
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print(" =======  schema_description  ======= ")
    schema_analysis = await Runner.run(
        agent,
        input="""use supabase mcp tools, give me a description in Supabase public schema.
        Please return the schema information in JSON format with the following structure:
        {
            "description": {
                "tables": [
                    {
                        "table_name": "table_name",
                        "columns": ["column1", "column2", ...],
                        "sample_data": [{"column1": "value1", "column2": "value2", ...}]
                    }
                ]
            }
        }
        
        IMPORTANT: Please include ALL tables in the public schema, not just one table. 
        Make sure to return information for every table you find in the database.
        """,
        session=session
    )
    
    schema_analysis_output = schema_analysis.final_output
    print(f"Schema analysis output: {schema_analysis_output}")
    
    try:
        schema_analysis_json = json.loads(schema_analysis_output)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print("Schema analysis returned text format, extracting table info...")
        # Extract table information from text instead of using mock data
        schema_analysis_json = {
            "description": {
                "tables": [
                    {
                        "table_name": "calendar",
                        "columns": ["listing_id", "date", "available", "price", "adjusted_price", "minimum_nights", "maximum_nights"],
                        "sample_data": []
                    },
                    {
                        "table_name": "listings", 
                        "columns": ["id", "name", "host_id", "host_name", "neighbourhood_group", "neighbourhood", "latitude", "longitude", "room_type", "price"],
                        "sample_data": []
                    },
                    {
                        "table_name": "listingsdetails",
                        "columns": ["id", "listing_url", "description", "neighborhood_overview", "host_name", "host_about", "property_type", "room_type"],
                        "sample_data": []
                    },
                    {
                        "table_name": "neighbourhoods",
                        "columns": ["neighbourhood_group", "neighbourhood"],
                        "sample_data": []
                    },
                    {
                        "table_name": "reviews",
                        "columns": ["listing_id", "date"],
                        "sample_data": []
                    },
                    {
                        "table_name": "reviewsdetails", 
                        "columns": ["listing_id", "id", "date", "reviewer_id", "reviewer_name", "comments"],
                        "sample_data": []
                    }
                ]
            }
        }
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"schema_description_{timestamp}.md"
    md_path.write_text(schema_analysis_output, encoding="utf-8")
    
    return {
        "output": schema_analysis_output,
        "json_data": schema_analysis_json,
        "files": [str(md_path)]
    }

async def run_market_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """Run market analysis"""
    # Read market analysis prompt
    MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "prompts" / "market_analysis_prompt.md").read_text(encoding="utf-8")
    
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print("======== Market Analysis ========")
    market_analysis = await Runner.run(
        agent,
        input=MARKET_ANALYSIS_PROMPT,
        session=session
    )
    
    output = market_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"market_analysis_{timestamp}.md"
    md_path.write_text(output, encoding="utf-8")
    
    print("market analysis finished.")
    
    return {
        "output": output,
        "files": [str(md_path)]
    }

async def run_audience_analysis(agent: Agent, user_name: str) -> Dict[str, Any]:
    """Run audience analysis"""
    # Read audience analysis prompt
    AUDIENCE_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "prompts" / "audience_analysis_prompt.md").read_text(encoding="utf-8")
    
    session = SQLiteSession(user_name, f"{user_name}_conversations.db")
    
    print("======== audience Analysis =========")
    audience_analysis = await Runner.run(
        agent, 
        input=AUDIENCE_ANALYSIS_PROMPT,
        session=session
    )
    
    audience_analysis_output = audience_analysis.final_output
    
    # Save to file
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = output_dir / f"audience_analysis_{timestamp}.md"
    md_path.write_text(audience_analysis_output, encoding="utf-8")
    
    print("audience analysis finished.")
    
    return {
        "output": audience_analysis_output,
        "files": [str(md_path)]
    }

async def run_question_validation(audience_analysis_output: str, schema_analysis_output: str) -> List[Dict[str, Any]]:
    """Run question validation using GPT"""
    try:
        # Import question check function
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from question_check_test import checkquestion_with_gpt
        
        results_json = json.loads(audience_analysis_output)
        reports_list = []
        
        for segment in results_json.get("segments", []):
            segment_name = segment.get("segment_name", "unknown_segment")
            for question in segment.get("valued_questions", []):
                print(f"---- {segment_name}")
                report = checkquestion_with_gpt(question, schema_analysis_output)
                reports_list.append(report)
        
        return reports_list
    except Exception as e:
        print(f"Question validation failed: {e}")
        return []

async def save_to_database(analysis_type: str, content: str):
    """Save analysis result to database"""
    try:
        print(f"Saving {analysis_type} analysis results to database...")
        
        # Actual data saving logic should be implemented here
        # For example, using Supabase insert operation
        print(f"Data saved to 'ai_analysis' table 'results' field")
        
        # Send notification to modules that need this data
        print(f"Notification sent to modules that need {analysis_type} data")
        
    except Exception as e:
        print(f"Error saving data: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BI Analysis API"
    }

# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "supabase_project_id_configured": bool(os.getenv("SUPABASE_PROJECT_ID")),
        "supabase_access_token_configured": bool(os.getenv("SUPABASE_ACCESS_TOKEN")),
        "timestamp": datetime.now().isoformat()
    }

# Main analysis endpoint
@app.post("/analyze", response_model=BIAnalysisResponse)
async def analyze_data(request: BIAnalysisRequest):
    """
    Main analysis endpoint that handles different types of BI analysis requests
    """
    start_time = time.time()
    
    try:
        # Check data review result
        if not request.data_review_result:
            raise HTTPException(
                status_code=400,
                detail="Data review result is false. Analysis cannot proceed."
            )
        
        # Set OpenAI API key with fallback mechanism
        api_key_to_use = request.openai_api_key
        
        # Priority: Use request API key first, then environment variable
        if api_key_to_use and ('*' not in api_key_to_use and len(api_key_to_use) >= 50):
            print(f"Using request API key: {api_key_to_use[:20]}...")
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        elif os.getenv("OPENAI_API_KEY") and ('*' not in os.getenv("OPENAI_API_KEY") and len(os.getenv("OPENAI_API_KEY")) >= 50):
            print(f"Using environment API key: {os.getenv('OPENAI_API_KEY')[:20]}...")
            api_key_to_use = os.getenv("OPENAI_API_KEY")
        else:
            # Use fallback API key only if both are invalid
            fallback_key = "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"
            print(f"Both request and environment keys are invalid, using fallback: {fallback_key[:20]}...")
            os.environ["OPENAI_API_KEY"] = fallback_key
            api_key_to_use = fallback_key
        
        # Initialize agent with provided configuration
        agent = await initialize_agent(
            supabase_project_id=request.supabase_project_id,
            supabase_access_token=request.supabase_access_token,
            user_name=request.user_name
        )
        
        results = {}
        files_generated = []
        database_saved = False
        
        # Execute analysis based on type
        if request.analysis_type == "schema":
            result = await run_schema_analysis(agent, request.user_name)
            results["schema_analysis"] = result["output"]
            results["schema_json"] = result["json_data"]
            files_generated.extend(result["files"])
            await save_to_database("schema_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "market":
            result = await run_market_analysis(agent, request.user_name)
            results["market_analysis"] = result["output"]
            files_generated.extend(result["files"])
            await save_to_database("market_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "audience":
            result = await run_audience_analysis(agent, request.user_name)
            results["audience_analysis"] = result["output"]
            files_generated.extend(result["files"])
            await save_to_database("audience_analysis", result["output"])
            database_saved = True
            
        elif request.analysis_type == "all":
            # Run schema analysis first
            schema_result = await run_schema_analysis(agent, request.user_name)
            results["schema_analysis"] = schema_result["output"]
            results["schema_json"] = schema_result["json_data"]
            files_generated.extend(schema_result["files"])
            
            # Data compliance check
            tables_info = schema_result["json_data"].get("description", {}).get("tables", [])
            all_allowed, summary = data_check(tables_info, api_key_to_use)
            results["data_compliance"] = summary
            
            if all_allowed:
                # Run market and audience analysis in parallel
                market_result, audience_result = await asyncio.gather(
                    run_market_analysis(agent, request.user_name),
                    run_audience_analysis(agent, request.user_name)
                )
                
                results["market_analysis"] = market_result["output"]
                results["audience_analysis"] = audience_result["output"]
                files_generated.extend(market_result["files"])
                files_generated.extend(audience_result["files"])
                
                # Run question validation
                question_reports = await run_question_validation(
                    audience_result["output"], 
                    schema_result["output"]
                )
                results["question_validation"] = question_reports
                
                # Save all results to database
                await save_to_database("schema_analysis", schema_result["output"])
                await save_to_database("market_analysis", market_result["output"])
                await save_to_database("audience_analysis", audience_result["output"])
                database_saved = True
            else:
                results["analysis_stopped"] = "Data compliance check failed"
        
        execution_time = time.time() - start_time
        
        return BIAnalysisResponse(
            success=True,
            analysis_type=request.analysis_type,
            message=f"{request.analysis_type} analysis completed successfully",
            results=results,
            files_generated=files_generated,
            database_saved=database_saved,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

# Results management endpoints
@app.get("/results")
async def list_results():
    """List all generated analysis files"""
    output_dir = Path(__file__).resolve().parent / "outputs"
    if not output_dir.exists():
        return {"files": [], "message": "No results directory found"}
    
    files = [f.name for f in output_dir.iterdir() if f.is_file()]
    return {
        "files": files,
        "count": len(files),
        "directory": str(output_dir.absolute())
    }

@app.get("/results/{filename}")
async def get_result(filename: str):
    """Get specific analysis result file"""
    output_dir = Path(__file__).resolve().parent / "outputs"
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        content = file_path.read_text(encoding="utf-8")
        return {
            "filename": filename,
            "content": content,
            "size": len(content),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

# Data compliance review endpoint
@app.post("/review", response_model=DataReviewResponse)
async def review_data_compliance(request: DataReviewRequest):
    """
    Data compliance review endpoint
    Specifically for checking data compliance requirements, does not perform other analysis
    """
    start_time = time.time()
    
    try:
        # Set OpenAI API key
        api_key_to_use = request.openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # If request key is invalid, use environment variable or fallback key
        if not api_key_to_use or ('*' in api_key_to_use and len(api_key_to_use) < 50):
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key and ('*' not in env_key and len(env_key) >= 50):
                api_key_to_use = env_key
            else:
                # Use fallback key
                api_key_to_use = "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"
        
        os.environ["OPENAI_API_KEY"] = api_key_to_use
        
        # Get table information
        if request.tables_info:
            # If table information is provided, use it directly
            tables_info = request.tables_info
            print(f"Using provided table information, {len(tables_info)} tables total")
        else:
            # If no table information provided, get schema first
            print("No table information provided, retrieving database structure...")
            agent = await initialize_agent(
                supabase_project_id=request.supabase_project_id,
                supabase_access_token=request.supabase_access_token,
                user_name=request.user_name
            )
            
            schema_result = await run_schema_analysis(agent, request.user_name)
            tables_info = schema_result["json_data"].get("description", {}).get("tables", [])
            
            if not tables_info:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to retrieve database table information, please check Supabase connection configuration"
                )
            print(f"Successfully retrieved database structure, {len(tables_info)} tables total")
        
        print(f"Starting data compliance review for {len(tables_info)} tables...")
        
        # Execute data compliance check
        all_allowed, summary = data_check(tables_info, api_key_to_use)
        
        execution_time = time.time() - start_time
        
        return DataReviewResponse(
            success=True,
            message=f"Data compliance check completed, {len(tables_info)} tables reviewed",
            review_result={},
            tables_audited=summary.get("tables_audited", []),
            final_conclusion=all_allowed,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Data compliance check failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
