from agency_swarm.tools import BaseTool
from pydantic import Field
from sqlalchemy import create_engine, text, inspect
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class SchemaAnalysisTool(BaseTool):
    """
    A comprehensive tool for analyzing database schema, including tables, columns, 
    relationships, indexes, and constraints with memory integration.
    """
    
    table_name: Optional[str] = Field(
        default=None,
        description="Specific table name to analyze. If None, analyzes all tables."
    )
    
    include_relationships: bool = Field(
        default=True,
        description="Whether to include foreign key relationships in the analysis."
    )
    
    include_indexes: bool = Field(
        default=True,
        description="Whether to include index information in the analysis."
    )

    def run(self) -> str:
        """
        Perform comprehensive schema analysis and store findings in memory.
        Returns detailed schema information in a formatted structure.
        """
        try:
            engine = self.agent.get_database_engine()
            memory = self.agent.get_memory_instance()
            
            if not engine:
                return "❌ Error: Database engine not initialized"
            
            inspector = inspect(engine)
            
            # Check if we have cached schema info
            if self.table_name:
                cached_info = memory.search(
                    f"table structure {self.table_name}",
                    user_id="system",
                    category="schema_info"
                )
            else:
                cached_info = memory.search(
                    "database schema overview",
                    user_id="system", 
                    category="schema_info"
                )
            
            result = {}
            
            # Get tables to analyze
            if self.table_name:
                if self.table_name not in inspector.get_table_names():
                    return f"❌ Error: Table '{self.table_name}' not found"
                tables_to_analyze = [self.table_name]
            else:
                tables_to_analyze = inspector.get_table_names()
            
            result['tables'] = {}
            all_foreign_keys = []
            
            # Analyze each table
            for table in tables_to_analyze:
                table_info = self._analyze_table(inspector, table)
                result['tables'][table] = table_info
                
                # Collect foreign keys for relationship mapping
                if table_info.get('foreign_keys'):
                    all_foreign_keys.extend([
                        {
                            'source_table': table,
                            'source_column': fk['constrained_columns'][0],
                            'target_table': fk['referred_table'],
                            'target_column': fk['referred_columns'][0]
                        }
                        for fk in table_info['foreign_keys']
                    ])
            
            # Build relationship map
            if self.include_relationships and not self.table_name:
                result['relationships'] = self._build_relationship_map(all_foreign_keys)
            
            # Store schema information in memory
            self._store_schema_in_memory(memory, result, tables_to_analyze)
            
            # Format response
            return self._format_schema_response(result)
            
        except Exception as e:
            error_msg = f"Schema analysis failed: {str(e)}"
            logger.error(error_msg)
            
            memory = self.agent.get_memory_instance()
            memory.add(
                error_msg,
                user_id="system",
                category="error_log",
                metadata={"error_type": "schema_analysis_error", "tool": "SchemaAnalysisTool"}
            )
            
            return f"❌ **Schema Analysis Error:**\n{str(e)}"
    
    def _analyze_table(self, inspector, table_name: str) -> Dict[str, Any]:
        """Analyze a single table and return comprehensive information"""
        table_info = {
            'columns': [],
            'primary_keys': [],
            'foreign_keys': [],
            'indexes': [],
            'row_count': None
        }
        
        # Get columns
        columns = inspector.get_columns(table_name)
        for col in columns:
            column_info = {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': str(col['default']) if col['default'] else None,
                'autoincrement': col.get('autoincrement', False)
            }
            table_info['columns'].append(column_info)
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint:
            table_info['primary_keys'] = pk_constraint['constrained_columns']
        
        # Get foreign keys
        if self.include_relationships:
            foreign_keys = inspector.get_foreign_keys(table_name)
            table_info['foreign_keys'] = foreign_keys
        
        # Get indexes
        if self.include_indexes:
            indexes = inspector.get_indexes(table_name)
            for idx in indexes:
                index_info = {
                    'name': idx['name'],
                    'columns': idx['column_names'],
                    'unique': idx['unique']
                }
                table_info['indexes'].append(index_info)
        
        # Get approximate row count
        try:
            engine = self.agent.get_database_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                table_info['row_count'] = result.fetchone()[0]
        except:
            table_info['row_count'] = "Unable to determine"
        
        return table_info
    
    def _build_relationship_map(self, foreign_keys: List[Dict]) -> Dict[str, List[Dict]]:
        """Build a comprehensive relationship map"""
        relationships = {}
        
        for fk in foreign_keys:
            source = fk['source_table']
            target = fk['target_table']
            
            if source not in relationships:
                relationships[source] = []
            
            relationships[source].append({
                'type': 'references',
                'target_table': target,
                'source_column': fk['source_column'],
                'target_column': fk['target_column']
            })
        
        return relationships
    
    def _store_schema_in_memory(self, memory, schema_result: Dict, tables: List[str]):
        """Store schema analysis results in memory for future reference"""
        try:
            # Store overall schema summary
            table_summaries = []
            for table_name, table_info in schema_result['tables'].items():
                summary = f"{table_name} ({len(table_info['columns'])} columns, ~{table_info['row_count']} rows)"
                table_summaries.append(summary)
            
            overall_summary = f"Schema analysis completed for {len(tables)} tables: {', '.join(table_summaries)}"
            memory.add(
                overall_summary,
                user_id="system",
                category="schema_info",
                metadata={"analysis_type": "overview", "table_count": len(tables)}
            )
            
            # Store individual table details
            for table_name, table_info in schema_result['tables'].items():
                table_detail = f"Table {table_name}: {len(table_info['columns'])} columns "
                table_detail += f"({', '.join([col['name'] for col in table_info['columns'][:5]])})"
                if len(table_info['columns']) > 5:
                    table_detail += f" and {len(table_info['columns']) - 5} more"
                
                if table_info['primary_keys']:
                    table_detail += f". Primary key: {', '.join(table_info['primary_keys'])}"
                
                memory.add(
                    table_detail,
                    user_id="system",
                    category="schema_info",
                    metadata={"table_name": table_name, "analysis_type": "table_detail"}
                )
            
        except Exception as e:
            logger.error(f"Failed to store schema in memory: {e}")
    
    def _format_schema_response(self, result: Dict) -> str:
        """Format the schema analysis results for display"""
        response = "📊 **Database Schema Analysis**\n\n"
        
        for table_name, table_info in result['tables'].items():
            response += f"🏷️ **Table: {table_name}**\n"
            response += f"   Rows: ~{table_info['row_count']}\n\n"
            
            # Columns
            response += "   **Columns:**\n"
            for col in table_info['columns']:
                pk_indicator = " 🔑" if col['name'] in table_info['primary_keys'] else ""
                nullable = " (nullable)" if col['nullable'] else " (not null)"
                response += f"   - {col['name']}: {col['type']}{nullable}{pk_indicator}\n"
            
            # Foreign Keys
            if table_info['foreign_keys']:
                response += "\n   **Foreign Keys:**\n"
                for fk in table_info['foreign_keys']:
                    source_cols = ', '.join(fk['constrained_columns'])
                    target_cols = ', '.join(fk['referred_columns'])
                    response += f"   - {source_cols} → {fk['referred_table']}.{target_cols}\n"
            
            # Indexes
            if table_info['indexes']:
                response += "\n   **Indexes:**\n"
                for idx in table_info['indexes']:
                    unique_indicator = " (unique)" if idx['unique'] else ""
                    response += f"   - {idx['name']}: {', '.join(idx['columns'])}{unique_indicator}\n"
            
            response += "\n" + "="*50 + "\n\n"
        
        # Relationships summary
        if 'relationships' in result:
            response += "🔗 **Table Relationships:**\n"
            for source_table, relationships in result['relationships'].items():
                response += f"   {source_table}:\n"
                for rel in relationships:
                    response += f"   → {rel['target_table']} via {rel['source_column']}\n"
        
        return response


if __name__ == "__main__":
    print("SchemaAnalysisTool - Use within DatabaseAnalysisAgent context")