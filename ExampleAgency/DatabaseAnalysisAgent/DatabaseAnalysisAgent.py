from agency_swarm import Agent
from mem0 import Memory
import os
import logging
from typing import Optional
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseAnalysisAgent(Agent):
    def __init__(self):
        super().__init__(
            name="DatabaseAnalysisAgent",
            description="An intelligent database analysis agent with memory capabilities, specialized in PostgreSQL operations, query optimization, and learning from interactions.",
            instructions="./instructions.md",
            tools_folder="./tools",
            model="gpt-4o",
        )
        
        # Initialize mem0 for memory management
        self.memory = Memory()
        
        # Database configuration
        self.db_url = "postgresql://postgres:YhqtIWPZOrFzkeoYebnawGoTWdgfsMIx@trolley.proxy.rlwy.net:25473/railway"
        self.engine = None
        
        # Initialize database connection and memory
        self._initialize_database()
        self._initialize_memory()
    
    def _initialize_database(self):
        """Initialize database connection and perform initial setup"""
        try:
            self.engine = create_engine(self.db_url, pool_pre_ping=True, pool_recycle=300)
            logger.info("Database engine created successfully")
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version[:50]}...")
                
                # Store database connection info in memory
                self.memory.add(
                    f"Connected to PostgreSQL database at {self.db_url}. Version: {version[:100]}",
                    user_id="system",
                    category="database_connection"
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.memory.add(
                f"Database connection failed: {str(e)}",
                user_id="system", 
                category="error_log"
            )
            raise
    
    def _initialize_memory(self):
        """Initialize memory categories and load existing knowledge"""
        try:
            # Create memory categories for different types of information
            categories = [
                "schema_info",
                "query_patterns", 
                "user_preferences",
                "error_solutions",
                "performance_insights"
            ]
            
            for category in categories:
                self.memory.add(
                    f"Initialized memory category: {category}",
                    user_id="system",
                    category=category
                )
            
            logger.info("Memory system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory: {e}")
    
    def get_memory_context(self, query: str, category: Optional[str] = None) -> str:
        """Retrieve relevant memories for a given query"""
        try:
            memories = self.memory.search(query, user_id="system", category=category)
            if memories:
                context = "Relevant past experiences:\n"
                for i, memory in enumerate(memories[:5], 1):  # Limit to top 5 memories
                    context += f"{i}. {memory['memory']}\n"
                return context
            return ""
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return ""
    
    def learn_from_interaction(self, interaction_type: str, content: str, category: str):
        """Store learning from interactions"""
        try:
            self.memory.add(
                content,
                user_id="system",
                category=category,
                metadata={"interaction_type": interaction_type}
            )
            logger.info(f"Stored learning in category {category}: {interaction_type}")
        except Exception as e:
            logger.error(f"Failed to store learning: {e}")
    
    def get_database_engine(self):
        """Get the database engine for use in tools"""
        return self.engine
    
    def get_memory_instance(self):
        """Get the memory instance for use in tools"""
        return self.memory