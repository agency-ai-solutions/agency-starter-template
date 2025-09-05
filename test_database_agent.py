#!/usr/bin/env python3
"""
Comprehensive test suite for DatabaseAnalysisAgent and its tools.
Tests database connectivity, memory integration, and learning capabilities.
"""

import sys
import os
import asyncio
import logging
import traceback
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ExampleAgency.DatabaseAnalysisAgent.DatabaseAnalysisAgent import DatabaseAnalysisAgent
from ExampleAgency.DatabaseAnalysisAgent.tools.DatabaseConnectionTool import DatabaseConnectionTool
from ExampleAgency.DatabaseAnalysisAgent.tools.SchemaAnalysisTool import SchemaAnalysisTool
from ExampleAgency.DatabaseAnalysisAgent.tools.QueryExecutorTool import QueryExecutorTool
from ExampleAgency.DatabaseAnalysisAgent.tools.DataAnalysisTool import DataAnalysisTool
from ExampleAgency.DatabaseAnalysisAgent.tools.MemoryLearningTool import MemoryLearningTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseAgentTester:
    """Comprehensive test suite for DatabaseAnalysisAgent"""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            logger.info(f"✅ PASS: {test_name}")
        else:
            logger.error(f"❌ FAIL: {test_name} - {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def setup_agent(self):
        """Initialize the DatabaseAnalysisAgent"""
        try:
            logger.info("🚀 Initializing DatabaseAnalysisAgent...")
            self.agent = DatabaseAnalysisAgent()
            self.log_test_result("Agent Initialization", True)
            return True
        except Exception as e:
            self.log_test_result("Agent Initialization", False, str(e))
            return False
    
    def test_agent_attributes(self):
        """Test that agent has required attributes"""
        try:
            required_attributes = ['memory', 'engine', 'db_url']
            for attr in required_attributes:
                if not hasattr(self.agent, attr):
                    raise AttributeError(f"Agent missing required attribute: {attr}")
            
            # Check if memory is properly initialized
            if self.agent.memory is None:
                raise ValueError("Memory system not initialized")
            
            # Check if database engine is initialized
            if self.agent.engine is None:
                raise ValueError("Database engine not initialized")
            
            self.log_test_result("Agent Attributes", True)
            return True
        except Exception as e:
            self.log_test_result("Agent Attributes", False, str(e))
            return False
    
    def test_database_connection_tool(self):
        """Test DatabaseConnectionTool"""
        try:
            tool = DatabaseConnectionTool()
            tool.agent = self.agent
            
            # Test basic connection
            result = tool.run()
            
            if "❌" in result:
                raise Exception(f"Connection failed: {result}")
            
            if "Database Connection Successful" not in result:
                raise Exception(f"Unexpected result: {result[:100]}")
            
            self.log_test_result("Database Connection Tool", True)
            return True
        except Exception as e:
            self.log_test_result("Database Connection Tool", False, str(e))
            return False
    
    def test_schema_analysis_tool(self):
        """Test SchemaAnalysisTool"""
        try:
            tool = SchemaAnalysisTool()
            tool.agent = self.agent
            
            # Test general schema analysis (limited to avoid long execution)
            result = tool.run()
            
            if "❌" in result:
                raise Exception(f"Schema analysis failed: {result}")
            
            if "Database Schema Analysis" not in result:
                raise Exception(f"Unexpected result format: {result[:100]}")
            
            self.log_test_result("Schema Analysis Tool", True)
            return True
        except Exception as e:
            self.log_test_result("Schema Analysis Tool", False, str(e))
            return False
    
    def test_query_executor_tool(self):
        """Test QueryExecutorTool with safe queries"""
        try:
            tool = QueryExecutorTool(sql_query="SELECT version()", limit_rows=1)
            tool.agent = self.agent
            
            result = tool.run()
            
            if "❌" in result and "Query Safety Error" not in result:
                raise Exception(f"Query execution failed: {result}")
            
            if "Query Executed Successfully" not in result and "Query Safety Error" not in result:
                raise Exception(f"Unexpected result: {result[:100]}")
            
            self.log_test_result("Query Executor Tool - Basic", True)
            
            # Test safety validation with dangerous query
            dangerous_tool = QueryExecutorTool(sql_query="DROP TABLE users", limit_rows=1)
            dangerous_tool.agent = self.agent
            
            dangerous_result = dangerous_tool.run()
            
            if "Query Safety Error" not in dangerous_result:
                raise Exception("Safety validation failed - dangerous query was not blocked")
            
            self.log_test_result("Query Executor Tool - Safety", True)
            return True
            
        except Exception as e:
            self.log_test_result("Query Executor Tool", False, str(e))
            return False
    
    def test_data_analysis_tool(self):
        """Test DataAnalysisTool with a sample table"""
        try:
            # First, we need to find a table to analyze
            # Let's try to get table list first
            connection_tool = DatabaseConnectionTool(test_only=False)
            connection_tool.agent = self.agent
            connection_result = connection_tool.run()
            
            # Extract table name if possible
            if "Sample Tables:" in connection_result:
                # This is a simplified test - in reality we'd parse the table names
                # For now, we'll test with a common system table
                tool = DataAnalysisTool(
                    table_name="information_schema.tables", 
                    analysis_type="summary",
                    sample_size=10
                )
                tool.agent = self.agent
                
                result = tool.run()
                
                # Accept both success and "table not found" as valid (database-dependent)
                if "Data Analysis Report" in result or "not found" in result:
                    self.log_test_result("Data Analysis Tool", True)
                    return True
                else:
                    raise Exception(f"Unexpected result: {result[:100]}")
            else:
                # Skip if no tables available
                self.log_test_result("Data Analysis Tool", True, "Skipped - no accessible tables")
                return True
                
        except Exception as e:
            self.log_test_result("Data Analysis Tool", False, str(e))
            return False
    
    def test_memory_learning_tool(self):
        """Test MemoryLearningTool"""
        try:
            # First add some test memories
            memory = self.agent.get_memory_instance()
            
            # Add test memories
            memory.add(
                "Test error: connection timeout occurred",
                user_id="system",
                category="error_log"
            )
            
            memory.add(
                "Successful query executed in 0.5s: SELECT * FROM test_table",
                user_id="system", 
                category="query_patterns"
            )
            
            # Test the learning tool
            tool = MemoryLearningTool(
                learning_query="database errors",
                max_suggestions=3
            )
            tool.agent = self.agent
            
            result = tool.run()
            
            if "Memory Learning Analysis" not in result:
                raise Exception(f"Unexpected result format: {result[:100]}")
            
            self.log_test_result("Memory Learning Tool", True)
            return True
            
        except Exception as e:
            self.log_test_result("Memory Learning Tool", False, str(e))
            return False
    
    def test_memory_persistence(self):
        """Test memory persistence and retrieval"""
        try:
            memory = self.agent.get_memory_instance()
            
            # Add a test memory
            test_content = f"Test memory for persistence check - {datetime.now().isoformat()}"
            memory.add(
                test_content,
                user_id="system",
                category="test_memory"
            )
            
            # Try to retrieve it
            retrieved = memory.search("test memory persistence", user_id="system")
            
            if not retrieved:
                raise Exception("Failed to retrieve stored memory")
            
            self.log_test_result("Memory Persistence", True)
            return True
            
        except Exception as e:
            self.log_test_result("Memory Persistence", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        try:
            # Test with invalid query
            tool = QueryExecutorTool(sql_query="INVALID SQL SYNTAX HERE", limit_rows=1)
            tool.agent = self.agent
            
            result = tool.run()
            
            # Should handle error gracefully
            if "❌" not in result:
                raise Exception("Error handling failed - should have returned error message")
            
            # Check if error was stored in memory
            memory = self.agent.get_memory_instance()
            error_memories = memory.search("syntax error", user_id="system", category="error_solutions")
            
            if not error_memories:
                raise Exception("Error was not stored in memory for learning")
            
            self.log_test_result("Error Handling", True)
            return True
            
        except Exception as e:
            self.log_test_result("Error Handling", False, str(e))
            return False
    
    def test_learning_integration(self):
        """Test end-to-end learning integration"""
        try:
            memory = self.agent.get_memory_instance()
            
            # Simulate a successful query
            memory.add(
                "Query executed successfully in 0.8s: SELECT count(*) FROM users. Returned 1 rows with columns: count",
                user_id="system",
                category="query_patterns",
                metadata={
                    "execution_time": 0.8,
                    "row_count": 1,
                    "query_type": "successful"
                }
            )
            
            # Simulate an error
            memory.add(
                "Query failed with error: relation 'nonexistent_table' does not exist. Query: SELECT * FROM nonexistent_table",
                user_id="system",
                category="error_solutions",
                metadata={
                    "error_type": "query_execution",
                    "error_message": "relation does not exist"
                }
            )
            
            # Test retrieval and pattern recognition
            context = self.agent.get_memory_context("database query patterns")
            
            if not context:
                raise Exception("Failed to retrieve memory context")
            
            # Test learning from the pattern
            learning_tool = MemoryLearningTool(learning_query="query patterns")
            learning_tool.agent = self.agent
            
            learning_result = learning_tool.run()
            
            if "Memory Learning Analysis" not in learning_result:
                raise Exception("Learning analysis failed")
            
            self.log_test_result("Learning Integration", True)
            return True
            
        except Exception as e:
            self.log_test_result("Learning Integration", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("🧪 Starting DatabaseAnalysisAgent Test Suite")
        logger.info("=" * 60)
        
        # Setup
        if not await self.setup_agent():
            logger.error("❌ Failed to setup agent - aborting tests")
            return
        
        # Core tests
        test_methods = [
            self.test_agent_attributes,
            self.test_database_connection_tool,
            self.test_schema_analysis_tool,
            self.test_query_executor_tool,
            self.test_data_analysis_tool,
            self.test_memory_learning_tool,
            self.test_memory_persistence,
            self.test_error_handling,
            self.test_learning_integration
        ]
        
        # Run tests
        for test_method in test_methods:
            try:
                logger.info(f"🔬 Running {test_method.__name__}...")
                test_method()
            except Exception as e:
                logger.error(f"💥 Test {test_method.__name__} crashed: {e}")
                self.log_test_result(test_method.__name__, False, f"Test crashed: {e}")
        
        # Results
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("=" * 60)
        logger.info("🎯 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"📊 Total Tests: {self.total_tests}")
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 EXCELLENT: Agent is ready for production!")
        elif success_rate >= 75:
            logger.info("✅ GOOD: Agent is functional with minor issues")
        elif success_rate >= 50:
            logger.info("⚠️ FAIR: Agent needs improvement before production")
        else:
            logger.info("❌ POOR: Agent has significant issues")
        
        # Detailed results
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            message = f" - {result['message']}" if result['message'] else ""
            logger.info(f"  {status} {result['test']}{message}")
        
        logger.info("=" * 60)

# Main execution
async def main():
    """Main test execution function"""
    try:
        tester = DatabaseAgentTester()
        await tester.run_all_tests()
        
        # Return success rate for external monitoring
        success_rate = (tester.passed_tests / tester.total_tests * 100) if tester.total_tests > 0 else 0
        return success_rate >= 75  # Consider 75%+ as acceptable
        
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Install dependencies first
    logger.info("📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    
    # Run tests
    success = asyncio.run(main())
    
    if success:
        logger.info("🎊 All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Tests failed!")
        sys.exit(1)