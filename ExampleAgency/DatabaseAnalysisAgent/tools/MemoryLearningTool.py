from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class MemoryLearningTool(BaseTool):
    """
    A specialized tool for learning from past interactions, analyzing error patterns,
    and providing intelligent suggestions based on accumulated memory.
    """
    
    learning_query: str = Field(
        ...,
        description="Query or topic to learn from memory (e.g., 'SQL errors', 'slow queries', 'table analysis')"
    )
    
    category_filter: Optional[str] = Field(
        default=None,
        description="Memory category to focus on: 'error_solutions', 'query_patterns', 'performance_insights', etc."
    )
    
    time_window_days: int = Field(
        default=30,
        description="Number of days to look back in memory history"
    )
    
    max_suggestions: int = Field(
        default=5,
        description="Maximum number of suggestions to return"
    )

    def run(self) -> str:
        """
        Analyze memory patterns and provide intelligent learning-based suggestions.
        Returns insights, patterns, and recommendations based on historical data.
        """
        try:
            memory = self.agent.get_memory_instance()
            
            if not memory:
                return "❌ Error: Memory system not initialized"
            
            # Search for relevant memories
            memories = self._search_relevant_memories(memory)
            
            if not memories:
                return f"🤔 No relevant memories found for query: '{self.learning_query}'"
            
            # Analyze patterns in memories
            analysis = self._analyze_memory_patterns(memories)
            
            # Generate intelligent suggestions
            suggestions = self._generate_learning_suggestions(analysis)
            
            # Store this learning session
            self._store_learning_session(memory, analysis, suggestions)
            
            # Format response
            return self._format_learning_response(analysis, suggestions, memories)
            
        except Exception as e:
            error_msg = f"Memory learning failed: {str(e)}"
            logger.error(error_msg)
            return f"❌ **Memory Learning Error:**\n{str(e)}"
    
    def _search_relevant_memories(self, memory) -> List[Dict]:
        """Search for memories relevant to the learning query"""
        try:
            # Primary search with category filter
            if self.category_filter:
                memories = memory.search(
                    self.learning_query,
                    user_id="system",
                    category=self.category_filter
                )
            else:
                memories = memory.search(
                    self.learning_query,
                    user_id="system"
                )
            
            # Filter by time window if needed
            if self.time_window_days > 0:
                cutoff_date = datetime.now() - timedelta(days=self.time_window_days)
                filtered_memories = []
                
                for mem in memories:
                    metadata = mem.get('metadata', {})
                    timestamp_str = metadata.get('timestamp')
                    
                    if timestamp_str:
                        try:
                            mem_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if mem_date.replace(tzinfo=None) >= cutoff_date:
                                filtered_memories.append(mem)
                        except:
                            # Include memories without valid timestamps
                            filtered_memories.append(mem)
                    else:
                        # Include memories without timestamps
                        filtered_memories.append(mem)
                
                return filtered_memories[:20]  # Limit to 20 most relevant
            
            return memories[:20]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def _analyze_memory_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in the retrieved memories"""
        analysis = {
            'total_memories': len(memories),
            'categories': {},
            'error_patterns': [],
            'success_patterns': [],
            'performance_insights': [],
            'common_themes': [],
            'time_distribution': {}
        }
        
        # Categorize memories
        for memory in memories:
            category = memory.get('category', 'unknown')
            if category not in analysis['categories']:
                analysis['categories'][category] = []
            analysis['categories'][category].append(memory)
        
        # Analyze error patterns
        error_memories = analysis['categories'].get('error_log', []) + \
                        analysis['categories'].get('error_solutions', [])
        
        for error_mem in error_memories:
            error_text = error_mem.get('memory', '')
            metadata = error_mem.get('metadata', {})
            
            # Extract common error patterns
            if 'connection' in error_text.lower():
                analysis['error_patterns'].append('Database connection issues')
            elif 'timeout' in error_text.lower():
                analysis['error_patterns'].append('Query timeout problems')
            elif 'syntax' in error_text.lower():
                analysis['error_patterns'].append('SQL syntax errors')
            elif 'permission' in error_text.lower():
                analysis['error_patterns'].append('Permission/access issues')
        
        # Analyze success patterns
        success_memories = analysis['categories'].get('query_patterns', [])
        for success_mem in success_memories:
            success_text = success_mem.get('memory', '')
            metadata = success_mem.get('metadata', {})
            
            # Extract execution time patterns
            exec_time = metadata.get('execution_time', 0)
            if exec_time and float(exec_time) < 1.0:
                analysis['success_patterns'].append(f"Fast query execution ({exec_time}s)")
            elif exec_time and float(exec_time) > 5.0:
                analysis['success_patterns'].append(f"Slow query identified ({exec_time}s)")
        
        # Analyze performance insights
        perf_memories = analysis['categories'].get('performance_insights', [])
        for perf_mem in perf_memories:
            insight_text = perf_mem.get('memory', '')
            if 'slow' in insight_text.lower():
                analysis['performance_insights'].append(insight_text[:100])
        
        # Find common themes using keyword frequency
        all_text = ' '.join([mem.get('memory', '') for mem in memories])
        common_words = self._extract_common_keywords(all_text)
        analysis['common_themes'] = common_words[:10]
        
        return analysis
    
    def _extract_common_keywords(self, text: str) -> List[str]:
        """Extract common keywords from text"""
        # Remove common SQL and system words
        stop_words = {
            'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'select', 'from', 'where', 'order', 'group', 'having', 'limit',
            'database', 'table', 'column', 'query', 'error', 'failed', 'success'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return most common
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _generate_learning_suggestions(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Generate intelligent suggestions based on memory analysis"""
        suggestions = []
        
        # Error-based suggestions
        error_patterns = analysis.get('error_patterns', [])
        if 'Database connection issues' in error_patterns:
            suggestions.append({
                'type': 'error_prevention',
                'priority': 'high',
                'title': 'Connection Reliability',
                'description': 'Consider implementing connection pooling and retry logic',
                'action': 'Review database connection settings and add resilience measures'
            })
        
        if 'Query timeout problems' in error_patterns:
            suggestions.append({
                'type': 'performance',
                'priority': 'medium',
                'title': 'Query Optimization',
                'description': 'Multiple queries have timed out - review query complexity',
                'action': 'Add query complexity analysis and suggest LIMIT clauses'
            })
        
        if 'SQL syntax errors' in error_patterns:
            suggestions.append({
                'type': 'quality',
                'priority': 'medium',
                'title': 'Query Validation',
                'description': 'Frequent syntax errors detected',
                'action': 'Implement better SQL validation and provide syntax examples'
            })
        
        # Performance-based suggestions
        perf_insights = analysis.get('performance_insights', [])
        if len(perf_insights) > 0:
            suggestions.append({
                'type': 'optimization',
                'priority': 'medium',
                'title': 'Performance Monitoring',
                'description': f'Found {len(perf_insights)} performance issues to address',
                'action': 'Review slow queries and suggest indexing strategies'
            })
        
        # Success pattern suggestions
        success_patterns = analysis.get('success_patterns', [])
        fast_queries = [s for s in success_patterns if 'Fast query' in s]
        if len(fast_queries) > 3:
            suggestions.append({
                'type': 'best_practice',
                'priority': 'low',
                'title': 'Query Templates',
                'description': f'Identified {len(fast_queries)} efficient query patterns',
                'action': 'Create query templates based on successful patterns'
            })
        
        # Data-driven suggestions based on categories
        categories = analysis.get('categories', {})
        if len(categories.get('schema_info', [])) > 5:
            suggestions.append({
                'type': 'optimization',
                'priority': 'low', 
                'title': 'Schema Caching',
                'description': 'Frequent schema queries detected',
                'action': 'Implement schema information caching to improve performance'
            })
        
        return suggestions[:self.max_suggestions]
    
    def _store_learning_session(self, memory, analysis: Dict, suggestions: List[Dict]):
        """Store this learning session for future reference"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Store learning summary
            summary = f"Memory learning session: analyzed {analysis['total_memories']} memories "
            summary += f"for query '{self.learning_query}'. Generated {len(suggestions)} suggestions."
            
            memory.add(
                summary,
                user_id="system",
                category="query_patterns",
                metadata={
                    "learning_session": True,
                    "query": self.learning_query,
                    "memories_analyzed": analysis['total_memories'],
                    "suggestions_count": len(suggestions),
                    "timestamp": timestamp
                }
            )
            
            # Store high-priority suggestions as insights
            for suggestion in suggestions:
                if suggestion['priority'] == 'high':
                    memory.add(
                        f"High-priority suggestion: {suggestion['title']} - {suggestion['description']}",
                        user_id="system",
                        category="performance_insights",
                        metadata={
                            "suggestion_type": suggestion['type'],
                            "priority": suggestion['priority'],
                            "from_learning": True
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Failed to store learning session: {e}")
    
    def _format_learning_response(self, analysis: Dict, suggestions: List[Dict], 
                                memories: List[Dict]) -> str:
        """Format the learning analysis response"""
        response = f"🧠 **Memory Learning Analysis**\n\n"
        response += f"🔍 **Query:** {self.learning_query}\n"
        response += f"📊 **Analyzed:** {analysis['total_memories']} memories"
        
        if self.time_window_days > 0:
            response += f" (last {self.time_window_days} days)"
        response += "\n\n"
        
        # Categories breakdown
        if analysis['categories']:
            response += "📂 **Memory Categories:**\n"
            for category, mems in analysis['categories'].items():
                response += f"   - {category}: {len(mems)} memories\n"
            response += "\n"
        
        # Error patterns
        if analysis['error_patterns']:
            response += "⚠️ **Error Patterns Detected:**\n"
            error_counts = {}
            for error in analysis['error_patterns']:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                response += f"   - {error}: {count} occurrences\n"
            response += "\n"
        
        # Performance insights
        if analysis['performance_insights']:
            response += "⚡ **Performance Insights:**\n"
            for insight in analysis['performance_insights'][:3]:
                response += f"   - {insight}...\n"
            response += "\n"
        
        # Common themes
        if analysis['common_themes']:
            response += "🎯 **Common Themes:**\n"
            for theme, count in analysis['common_themes'][:5]:
                response += f"   - {theme}: {count} mentions\n"
            response += "\n"
        
        # Suggestions
        if suggestions:
            response += "💡 **Learning-Based Suggestions:**\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion['priority'], "⚪")
                response += f"   **{i}. {suggestion['title']}** {priority_emoji}\n"
                response += f"      {suggestion['description']}\n"
                response += f"      *Action:* {suggestion['action']}\n\n"
        
        # Sample memories
        response += "📝 **Recent Relevant Memories:**\n"
        for i, memory in enumerate(memories[:3], 1):
            mem_text = memory.get('memory', '')[:80]
            response += f"   {i}. {mem_text}...\n"
        
        return response


if __name__ == "__main__":
    print("MemoryLearningTool - Use within DatabaseAnalysisAgent context")