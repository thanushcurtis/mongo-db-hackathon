"""
test_run.py — Integration Test for Agent Graph
==============================================
This script tests the entire LangGraph pipeline from Manager to Synthesis.
"""

import os
import asyncio
from dotenv import load_dotenv
from app.agents.graph import graph

load_dotenv()

async def run_test():
    print("🚀 Starting Test Run for 'thanush'...")
    
    config = {"configurable": {"thread_id": "test_thread_001"}}
    initial_state = {
        "user_id": "thanushcurtis",
        "chat_message": "How does my AAPL Holdings looks now?"
    }
    
    try:
        print("⏳ Invoking Agent Graph (this may take 30-60 seconds)...\n")
        # Run in a thread if it's blocking, but graph.invoke is usually fine here
        # result = graph.invoke(initial_state, config=config)
        result = None
        for step in graph.stream(initial_state, config=config):
            print("Finished step:", step.keys())
            result = list(step.values())[0]
        
        print("✅ Graph Execution Complete!")
        print("="*50)
        print("FINAL REPORT SUMMARY:")
        report = result.get("final_report", "No report found.")
        print(report[:2000] + "..." if len(report) > 2000 else report)
        print("="*50)
        
    except Exception as e:
        print(f"❌ Test Failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_test())
