#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo2 Package - AI Analysis Core Module

This package contains the core functionality for AI-powered data analysis
using OpenAI Agents and Supabase MCP tools.
"""

__version__ = "1.0.0"
__author__ = "AI Analysis Team"

# Import core functions for easy access
from .demo_2_core import (
    initialize_agent,
    run_schema_analysis,
    run_market_analysis,
    run_audience_analysis,
    save_to_database
)

__all__ = [
    "initialize_agent",
    "run_schema_analysis", 
    "run_market_analysis",
    "run_audience_analysis",
    "save_to_database"
]
