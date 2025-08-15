from agency_swarm.tools import BaseTool
from pydantic import Field
from sqlalchemy import create_engine, text, inspect
from typing import Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseConnectionTool(BaseTool):
    """
    A tool for testing database connections and retrieving basic database information.
    This tool validates connectivity and gathers initial database metadata.
    """
    
    test_only: bool = Field(
        default=False,
        description="If True, only test the connection without gathering detailed info."
    )

    def run(self) -> str:
        """
        Test database connection and gather basic information.
        Returns connection status and basic database metadata.
        """
        try:
            # Get database engine from parent agent
            engine = self.agent.get_database_engine()
            memory = self.agent.get_memory_instance()
            
            if not engine:
                error_msg = "Database engine not initialized"
                memory.add(
                    f"Connection test failed: {error_msg}",
                    user_id="system",
                    category="error_log"
                )
                return f"❌ Error: {error_msg}"
            
            # Test connection
            with engine.connect() as conn:
                # Basic connection test
                result = conn.execute(text("SELECT version(), current_database(), current_user"))
                version, database, user = result.fetchone()
                
                connection_info = {
                    "status": "connected",
                    "database": database,
                    "user": user,
                    "version": version[:100]  # Truncate for readability
                }
                
                if not self.test_only:
                    # Get additional database information
                    inspector = inspect(engine)
                    
                    # Get table count
                    tables = inspector.get_table_names()
                    connection_info["table_count"] = len(tables)
                    connection_info["tables"] = tables[:10]  # First 10 tables
                    
                    # Get schema information
                    schemas = inspector.get_schema_names()
                    connection_info["schemas"] = schemas
                    
                    # Store schema information in memory
                    schema_info = f"Database '{database}' has {len(tables)} tables: {', '.join(tables[:20])}{'...' if len(tables) > 20 else ''}"
                    memory.add(
                        schema_info,
                        user_id="system",
                        category="schema_info",
                        metadata={"database": database, "table_count": len(tables)}
                    )
                
                # Store successful connection in memory
                memory.add(
                    f"Successfully connected to database '{database}' as user '{user}'",
                    user_id="system",
                    category="database_connection",
                    metadata={"status": "success", "database": database}
                )
                
                # Format response
                response = f"✅ Database Connection Successful!\n\n"
                response += f"📊 **Database Info:**\n"
                response += f"- Database: {connection_info['database']}\n"
                response += f"- User: {connection_info['user']}\n"
                response += f"- Version: {connection_info['version']}\n"
                
                if not self.test_only:
                    response += f"- Tables: {connection_info['table_count']}\n"
                    response += f"- Schemas: {', '.join(connection_info['schemas'])}\n"
                    
                    if connection_info['tables']:
                        response += f"\n🏷️ **Sample Tables:**\n"
                        for table in connection_info['tables']:
                            response += f"- {table}\n"
                
                logger.info(f"Database connection successful: {database}")
                return response
                
        except Exception as e:
            error_msg = f"Database connection failed: {str(e)}"
            logger.error(error_msg)
            
            # Store error in memory for learning
            memory.add(
                error_msg,
                user_id="system",
                category="error_log",
                metadata={"error_type": "connection_error", "tool": "DatabaseConnectionTool"}
            )
            
            return f"❌ **Connection Error:**\n{str(e)}\n\nPlease check the database URL and credentials."


if __name__ == "__main__":
    # This would be used for testing if we had the agent context
    print("DatabaseConnectionTool - Use within DatabaseAnalysisAgent context")