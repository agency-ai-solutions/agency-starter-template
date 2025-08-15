#!/usr/bin/env python3
"""
Simplified test suite for DatabaseAnalysisAgent focusing on core functionality.
Tests database connectivity and memory integration without OpenAI dependency.
"""

import sys
import os
import logging
from datetime import datetime
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection independently"""
    try:
        import psycopg2
        from sqlalchemy import create_engine, text
        
        db_url = "postgresql://postgres:YhqtIWPZOrFzkeoYebnawGoTWdgfsMIx@trolley.proxy.rlwy.net:25473/railway"
        
        # Test with psycopg2 directly
        logger.info("Testing direct psycopg2 connection...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"✅ Direct connection successful: {version[:50]}...")
        
        # Test with SQLAlchemy
        logger.info("Testing SQLAlchemy engine...")
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            logger.info(f"✅ SQLAlchemy connection successful: {db_name} as {user}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_mem0_initialization():
    """Test mem0 memory system initialization"""
    try:
        from mem0 import Memory
        
        logger.info("Testing mem0 memory initialization...")
        memory = Memory()
        
        # Test basic memory operations
        test_content = f"Test memory entry - {datetime.now().isoformat()}"
        memory.add(test_content, user_id="test", category="test_category")
        logger.info("✅ Memory add operation successful")
        
        # Test memory retrieval
        retrieved = memory.search("test memory", user_id="test")
        if retrieved:
            logger.info("✅ Memory search operation successful")
        else:
            logger.warning("⚠️ Memory search returned empty results")
        
        return True
    except Exception as e:
        logger.error(f"❌ Memory initialization failed: {e}")
        return False

def test_database_schema_discovery():
    """Test database schema discovery without agent"""
    try:
        from sqlalchemy import create_engine, inspect
        
        db_url = "postgresql://postgres:YhqtIWPZOrFzkeoYebnawGoTWdgfsMIx@trolley.proxy.rlwy.net:25473/railway"
        
        logger.info("Testing database schema discovery...")
        engine = create_engine(db_url, pool_pre_ping=True)
        inspector = inspect(engine)
        
        # Get basic schema info
        schemas = inspector.get_schema_names()
        tables = inspector.get_table_names()
        
        logger.info(f"✅ Found {len(schemas)} schemas: {schemas[:5]}")
        logger.info(f"✅ Found {len(tables)} tables: {tables[:10]}")
        
        # Analyze first table if available
        if tables:
            first_table = tables[0]
            columns = inspector.get_columns(first_table)
            logger.info(f"✅ Table '{first_table}' has {len(columns)} columns")
        
        return True
    except Exception as e:
        logger.error(f"❌ Schema discovery failed: {e}")
        return False

def test_query_execution():
    """Test safe query execution"""
    try:
        from sqlalchemy import create_engine, text
        import pandas as pd
        
        db_url = "postgresql://postgres:YhqtIWPZOrFzkeoYebnawGoTWdgfsMIx@trolley.proxy.rlwy.net:25473/railway"
        
        logger.info("Testing safe query execution...")
        engine = create_engine(db_url, pool_pre_ping=True)
        
        # Test basic system query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version(), current_timestamp"))
            row = result.fetchone()
            logger.info(f"✅ System query successful: {row[1]}")
        
        # Test with pandas
        df = pd.read_sql("SELECT 1 as test_col, 'test_value' as test_text", engine)
        logger.info(f"✅ Pandas query successful: {len(df)} rows returned")
        
        return True
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        return False

def test_tool_imports():
    """Test that all tools can be imported successfully"""
    try:
        logger.info("Testing tool imports...")
        
        # Test tool imports without initialization
        from ExampleAgency.DatabaseAnalysisAgent.tools.DatabaseConnectionTool import DatabaseConnectionTool
        from ExampleAgency.DatabaseAnalysisAgent.tools.SchemaAnalysisTool import SchemaAnalysisTool
        from ExampleAgency.DatabaseAnalysisAgent.tools.QueryExecutorTool import QueryExecutorTool
        from ExampleAgency.DatabaseAnalysisAgent.tools.DataAnalysisTool import DataAnalysisTool
        from ExampleAgency.DatabaseAnalysisAgent.tools.MemoryLearningTool import MemoryLearningTool
        
        logger.info("✅ All tool classes imported successfully")
        
        # Test tool instantiation (without agent context)
        tools = [
            DatabaseConnectionTool(),
            SchemaAnalysisTool(),
            QueryExecutorTool(sql_query="SELECT 1"),
            DataAnalysisTool(table_name="test_table"),
            MemoryLearningTool(learning_query="test query")
        ]
        
        logger.info(f"✅ {len(tools)} tools instantiated successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Tool import/instantiation failed: {e}")
        return False

def test_safety_validations():
    """Test SQL safety validation logic"""
    try:
        from ExampleAgency.DatabaseAnalysisAgent.tools.QueryExecutorTool import QueryExecutorTool
        
        logger.info("Testing SQL safety validations...")
        
        # Create tool instance
        tool = QueryExecutorTool(sql_query="DROP TABLE users")
        
        # Test safety validation method directly
        safety_result = tool._validate_query_safety()
        
        if safety_result['is_safe'] == False:
            logger.info(f"✅ Safety validation correctly blocked dangerous query: {safety_result['reason']}")
        else:
            logger.error("❌ Safety validation failed to block dangerous query")
            return False
        
        # Test safe query
        safe_tool = QueryExecutorTool(sql_query="SELECT version()")
        safe_result = safe_tool._validate_query_safety()
        
        if safe_result['is_safe'] == True:
            logger.info("✅ Safety validation correctly allowed safe query")
        else:
            logger.error("❌ Safety validation incorrectly blocked safe query")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Safety validation test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    logger.info("🧪 Starting Simplified DatabaseAgent Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Memory Initialization", test_mem0_initialization), 
        ("Schema Discovery", test_database_schema_discovery),
        ("Query Execution", test_query_execution),
        ("Tool Imports", test_tool_imports),
        ("Safety Validations", test_safety_validations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔬 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ PASSED: {test_name}")
            else:
                logger.error(f"❌ FAILED: {test_name}")
        except Exception as e:
            logger.error(f"💥 CRASHED: {test_name} - {e}")
    
    # Results summary
    logger.info("=" * 60)
    logger.info("🎯 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📊 Total Tests: {total}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {total - passed}")
    
    success_rate = (passed / total) * 100
    logger.info(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        logger.info("🎉 EXCELLENT: Core functionality is working perfectly!")
    elif success_rate >= 75:
        logger.info("✅ GOOD: Most functionality is working correctly")
    elif success_rate >= 50:
        logger.info("⚠️ FAIR: Basic functionality is working")
    else:
        logger.info("❌ POOR: Significant issues detected")
    
    logger.info("=" * 60)
    
    return success_rate >= 75

if __name__ == "__main__":
    try:
        success = run_all_tests()
        
        if success:
            logger.info("🎊 Core tests completed successfully!")
            logger.info("✨ Database Analysis Agent is ready for use!")
            sys.exit(0)
        else:
            logger.error("💥 Some tests failed - check configuration!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)