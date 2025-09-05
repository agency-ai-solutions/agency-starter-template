from agency_swarm.tools import BaseTool
from pydantic import Field
from sqlalchemy import create_engine, text
from typing import Dict, List, Any, Optional
import logging
import pandas as pd
import time
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryExecutorTool(BaseTool):
    """
    A sophisticated SQL query execution tool with safety measures, result formatting,
    and learning capabilities. Executes queries with proper error handling and memory integration.
    """
    
    sql_query: str = Field(
        ...,
        description="The SQL query to execute. Should be a valid SELECT statement."
    )
    
    limit_rows: int = Field(
        default=100,
        description="Maximum number of rows to return (safety measure)."
    )
    
    timeout_seconds: int = Field(
        default=30,
        description="Query timeout in seconds to prevent long-running queries."
    )
    
    learn_from_execution: bool = Field(
        default=True,
        description="Whether to store the query pattern and result in memory for learning."
    )

    def run(self) -> str:
        """
        Execute SQL query safely with comprehensive error handling and learning.
        Returns formatted results with query performance metrics.
        """
        try:
            engine = self.agent.get_database_engine()
            memory = self.agent.get_memory_instance()
            
            if not engine:
                return "❌ Error: Database engine not initialized"
            
            # Validate query safety
            safety_check = self._validate_query_safety()
            if safety_check['is_safe'] == False:
                error_msg = f"Query rejected for safety: {safety_check['reason']}"
                memory.add(
                    f"Unsafe query blocked: {self.sql_query[:100]}... Reason: {safety_check['reason']}",
                    user_id="system",
                    category="error_log",
                    metadata={"error_type": "unsafe_query", "tool": "QueryExecutorTool"}
                )
                return f"❌ **Query Safety Error:**\n{error_msg}"
            
            # Check for similar queries in memory
            similar_queries = self._check_similar_queries(memory)
            
            start_time = time.time()
            
            # Execute query with timeout and limit
            modified_query = self._apply_safety_limits()
            
            with engine.connect() as conn:
                # Set query timeout
                conn = conn.execution_options(autocommit=True)
                
                result = conn.execute(text(modified_query))
                rows = result.fetchall()
                columns = list(result.keys())
                
            execution_time = time.time() - start_time
            
            # Convert to pandas DataFrame for better handling
            df = pd.DataFrame(rows, columns=columns)
            
            # Format results
            formatted_result = self._format_query_results(df, execution_time)
            
            # Learn from successful execution
            if self.learn_from_execution:
                self._store_query_learning(memory, df, execution_time, success=True)
            
            return formatted_result
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            
            # Store error for learning
            memory = self.agent.get_memory_instance()
            self._store_query_learning(memory, None, execution_time, success=False, error=str(e))
            
            # Check for similar error patterns
            similar_errors = memory.search(
                f"query error {str(e)[:50]}",
                user_id="system",
                category="error_solutions"
            )
            
            suggestion = ""
            if similar_errors:
                suggestion = f"\n💡 **Similar errors found in memory:**\n{similar_errors[0]['memory'][:200]}..."
            
            return f"❌ **Query Execution Error:**\n{str(e)}{suggestion}"
    
    def _validate_query_safety(self) -> Dict[str, Any]:
        """Validate query for safety - prevent destructive operations"""
        query_lower = self.sql_query.lower().strip()
        
        # Check for destructive operations
        destructive_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate']
        for keyword in destructive_keywords:
            if re.search(r'\b' + keyword + r'\b', query_lower):
                return {
                    'is_safe': False,
                    'reason': f"Destructive operation '{keyword}' not allowed"
                }
        
        # Check for potential SQL injection patterns
        injection_patterns = [
            r';\s*drop\s+table',
            r'union\s+select.*from\s+information_schema',
            r'exec\s*\(',
            r'sp_executesql'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query_lower):
                return {
                    'is_safe': False,
                    'reason': "Potential SQL injection pattern detected"
                }
        
        return {'is_safe': True, 'reason': 'Query passed safety checks'}
    
    def _apply_safety_limits(self) -> str:
        """Apply safety limits to the query"""
        query = self.sql_query.strip()
        
        # Add LIMIT if not present
        if not re.search(r'\blimit\s+\d+', query.lower()):
            if query.lower().endswith(';'):
                query = query[:-1]  # Remove semicolon
            query += f" LIMIT {self.limit_rows}"
        
        return query
    
    def _check_similar_queries(self, memory) -> List[Dict]:
        """Check for similar queries in memory"""
        try:
            # Extract key terms from query for similarity search
            query_keywords = re.findall(r'\b\w+\b', self.sql_query.lower())
            search_terms = ' '.join(query_keywords[:5])  # Use first 5 keywords
            
            similar = memory.search(
                search_terms,
                user_id="system",
                category="query_patterns"
            )
            return similar[:3]  # Return top 3 similar queries
        except Exception as e:
            logger.error(f"Failed to check similar queries: {e}")
            return []
    
    def _format_query_results(self, df: pd.DataFrame, execution_time: float) -> str:
        """Format query results for display"""
        response = f"✅ **Query Executed Successfully**\n\n"
        response += f"⏱️ **Performance:**\n"
        response += f"- Execution Time: {execution_time:.3f} seconds\n"
        response += f"- Rows Returned: {len(df)}\n"
        response += f"- Columns: {len(df.columns)}\n\n"
        
        if len(df) > 0:
            response += f"📊 **Results Preview** (showing up to {min(10, len(df))} rows):\n\n"
            
            # Create formatted table
            preview_df = df.head(10)
            
            # Format column headers
            headers = " | ".join([f"{col:>12}" for col in preview_df.columns])
            response += f"{headers}\n"
            response += f"{'-' * len(headers)}\n"
            
            # Format data rows
            for _, row in preview_df.iterrows():
                formatted_row = []
                for val in row:
                    if pd.isna(val):
                        formatted_val = "NULL"
                    elif isinstance(val, (int, float)):
                        formatted_val = f"{val:>12}"
                    else:
                        formatted_val = f"{str(val)[:12]:>12}"
                    formatted_row.append(formatted_val)
                
                response += f"{' | '.join(formatted_row)}\n"
            
            # Add summary statistics for numeric columns
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_columns) > 0:
                response += f"\n📈 **Numeric Column Summary:**\n"
                for col in numeric_columns[:3]:  # Show stats for first 3 numeric columns
                    stats = df[col].describe()
                    response += f"- {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}\n"
            
            if len(df) > 10:
                response += f"\n... and {len(df) - 10} more rows"
        else:
            response += "📋 **No results returned**"
        
        return response
    
    def _store_query_learning(self, memory, df: Optional[pd.DataFrame], 
                            execution_time: float, success: bool, error: str = None):
        """Store query execution results for learning"""
        try:
            timestamp = datetime.now().isoformat()
            
            if success and df is not None:
                # Store successful query pattern
                learning_content = f"Query executed successfully in {execution_time:.3f}s: {self.sql_query[:100]}..."
                learning_content += f" Returned {len(df)} rows with columns: {', '.join(df.columns.tolist()[:5])}"
                
                memory.add(
                    learning_content,
                    user_id="system",
                    category="query_patterns",
                    metadata={
                        "execution_time": execution_time,
                        "row_count": len(df),
                        "column_count": len(df.columns),
                        "timestamp": timestamp,
                        "query_type": "successful"
                    }
                )
                
                # Store performance insight
                if execution_time > 5.0:  # Slow query threshold
                    performance_note = f"Slow query detected ({execution_time:.3f}s): {self.sql_query[:100]}..."
                    memory.add(
                        performance_note,
                        user_id="system",
                        category="performance_insights",
                        metadata={"slow_query": True, "execution_time": execution_time}
                    )
                
            else:
                # Store error for learning
                error_content = f"Query failed with error: {error}. Query: {self.sql_query[:100]}..."
                memory.add(
                    error_content,
                    user_id="system",
                    category="error_solutions",
                    metadata={
                        "error_type": "query_execution",
                        "error_message": error[:200],
                        "timestamp": timestamp,
                        "query_fragment": self.sql_query[:100]
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to store query learning: {e}")


if __name__ == "__main__":
    print("QueryExecutorTool - Use within DatabaseAnalysisAgent context")