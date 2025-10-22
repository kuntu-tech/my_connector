#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis API - FastAPI wrapper for demo-2.py script
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Any, Optional
import asyncio
import time
import os
from datetime import datetime
from pathlib import Path

# Import the core functionality from demo2 package
from demo2 import (
    initialize_agent,
    run_schema_analysis,
    run_market_analysis, 
    run_audience_analysis,
    save_to_database
)

app = FastAPI(
    title="AI Analysis API",
    version="1.0.0",
    description="A FastAPI service for AI-powered data analysis using OpenAI Agents and Supabase MCP tools."
)

# Request Models
class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analysis_type: Literal["schema", "market", "audience", "all"] = Field(
        ..., 
        description="Type of analysis to perform"
    )
    supabase_project_url: str = Field(
        ..., 
        description="Supabase project URL (MCP format)"
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

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    success: bool
    analysis_type: str
    message: str
    results: Dict[str, Any] = {}
    files_generated: List[str] = []
    database_saved: bool = False
    execution_time: float
    timestamp: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Analysis API"
    }

# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "supabase_project_url_configured": bool(os.getenv("SUPABASE_PROJECT_URL")),
        "supabase_access_token_configured": bool(os.getenv("SUPABASE_ACCESS_TOKEN")),
        "timestamp": datetime.now().isoformat()
    }

# Main analysis endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """
    Main analysis endpoint that handles different types of analysis requests
    """
    start_time = time.time()
    
    try:
        # Check data review result
        if not request.data_review_result:
            raise HTTPException(
                status_code=400,
                detail="Data review result is false. Analysis cannot proceed."
            )
        
        # Debug: Print environment variables
        print("=" * 60)
        print("DEBUG: API Key Analysis")
        print("=" * 60)
        
        # Check environment variable first
        env_api_key = os.getenv("OPENAI_API_KEY")
        print(f"Environment OPENAI_API_KEY: {env_api_key}")
        print(f"Environment key length: {len(env_api_key) if env_api_key else 0}")
        print(f"Environment key contains asterisks: {'*' in env_api_key if env_api_key else False}")
        
        # Check request API key
        request_api_key = request.openai_api_key
        print(f"Request OPENAI_API_KEY: {request_api_key}")
        print(f"Request key length: {len(request_api_key) if request_api_key else 0}")
        print(f"Request key contains asterisks: {'*' in request_api_key if request_api_key else False}")
        
        # Set OpenAI API key with fallback mechanism
        api_key_to_use = request.openai_api_key
        
        # Priority: Use request API key first, then environment variable
        if api_key_to_use and ('*' not in api_key_to_use and len(api_key_to_use) >= 50):
            print(f"Using request API key: {api_key_to_use[:20]}...")
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        elif env_api_key and ('*' not in env_api_key and len(env_api_key) >= 50):
            print(f"Using environment API key: {env_api_key[:20]}...")
            os.environ["OPENAI_API_KEY"] = env_api_key
            api_key_to_use = env_api_key
        else:
            # Use fallback API key only if both are invalid
            fallback_key = "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"
            print(f"Both request and environment keys are invalid, using fallback: {fallback_key[:20]}...")
            os.environ["OPENAI_API_KEY"] = fallback_key
            api_key_to_use = fallback_key
        
        # Set the API key to environment
        if api_key_to_use:
            os.environ["OPENAI_API_KEY"] = api_key_to_use
        
        # Final debug output
        final_api_key = os.getenv("OPENAI_API_KEY")
        print(f"Final API key to use: {final_api_key}")
        print(f"Final key length: {len(final_api_key) if final_api_key else 0}")
        print(f"Final key contains asterisks: {'*' in final_api_key if final_api_key else False}")
        print("=" * 60)
        
        # Initialize agent with provided configuration
        agent = await initialize_agent(
            supabase_project_url=request.supabase_project_url,
            supabase_access_token=request.supabase_access_token,
            user_name=request.user_name
        )
        
        results = {}
        files_generated = []
        # Note: headers are not available in Pydantic model, using default values
        headers = {"Content-Type": "application/json"}
        database_saved = False
        
        # Execute analysis based on type
        if request.analysis_type == "schema":
            result = await run_schema_analysis(agent, request.user_name)
            results["schema_analysis"] = result["output"]
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
            # Run all analyses in parallel
            tasks = [
                run_schema_analysis(agent, request.user_name),
                run_market_analysis(agent, request.user_name),
                run_audience_analysis(agent, request.user_name)
            ]
            
            schema_result, market_result, audience_result = await asyncio.gather(*tasks)
            
            results = {
                "schema_analysis": schema_result["output"],
                "market_analysis": market_result["output"],
                "audience_analysis": audience_result["output"]
            }
            
            files_generated.extend(schema_result["files"])
            files_generated.extend(market_result["files"])
            files_generated.extend(audience_result["files"])
            
            # Save all results to database
            await save_to_database("schema_analysis", schema_result["output"])
            await save_to_database("market_analysis", market_result["output"])
            await save_to_database("audience_analysis", audience_result["output"])
            database_saved = True
        
        execution_time = time.time() - start_time
        
        return AnalysisResponse(
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

# Batch analysis endpoint
@app.post("/analyze/batch", response_model=AnalysisResponse)
async def analyze_batch(requests: List[AnalysisRequest]):
    """
    Batch analysis endpoint for multiple requests
    """
    start_time = time.time()
    
    try:
        all_results = {}
        all_files = []
        database_saved = True
        
        # Process all requests
        for request in requests:
            if not request.data_review_result:
                continue
                
            # Initialize agent for this request
            agent = await initialize_agent(
                supabase_project_url=request.supabase_project_url,
                supabase_access_token=request.supabase_access_token,
                user_name=request.user_name
            )
            
            # Execute analysis
            if request.analysis_type == "schema":
                result = await run_schema_analysis(agent, request.user_name)
                all_results[f"schema_analysis_{request.user_name}"] = result["output"]
                all_files.extend(result["files"])
                await save_to_database("schema_analysis", result["output"])
                
            elif request.analysis_type == "market":
                result = await run_market_analysis(agent, request.user_name)
                all_results[f"market_analysis_{request.user_name}"] = result["output"]
                all_files.extend(result["files"])
                await save_to_database("market_analysis", result["output"])
                
            elif request.analysis_type == "audience":
                result = await run_audience_analysis(agent, request.user_name)
                all_results[f"audience_analysis_{request.user_name}"] = result["output"]
                all_files.extend(result["files"])
                await save_to_database("audience_analysis", result["output"])
        
        execution_time = time.time() - start_time
        
        return AnalysisResponse(
            success=True,
            analysis_type="batch",
            message=f"Batch analysis completed successfully for {len(requests)} requests",
            results=all_results,
            files_generated=all_files,
            database_saved=database_saved,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )

# Results management endpoints
@app.get("/results")
async def list_results():
    """List all generated analysis files"""
    output_dir = Path("outputs")
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
    output_dir = Path("outputs")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
