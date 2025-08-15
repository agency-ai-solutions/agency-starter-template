from agency_swarm.tools import BaseTool
from pydantic import Field
from sqlalchemy import create_engine, text
from typing import Dict, List, Any, Optional
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DataAnalysisTool(BaseTool):
    """
    A comprehensive data analysis tool that performs statistical analysis,
    data profiling, and generates insights with memory-backed recommendations.
    """
    
    table_name: str = Field(
        ...,
        description="Name of the table to analyze."
    )
    
    column_name: Optional[str] = Field(
        default=None,
        description="Specific column to analyze. If None, analyzes all columns."
    )
    
    analysis_type: str = Field(
        default="summary",
        description="Type of analysis: 'summary', 'detailed', 'correlation', 'distribution'"
    )
    
    sample_size: int = Field(
        default=1000,
        description="Number of rows to sample for analysis (performance optimization)."
    )

    def run(self) -> str:
        """
        Perform comprehensive data analysis and generate insights.
        Returns detailed statistical analysis with actionable recommendations.
        """
        try:
            engine = self.agent.get_database_engine()
            memory = self.agent.get_memory_instance()
            
            if not engine:
                return "❌ Error: Database engine not initialized"
            
            # Check for previous analysis in memory
            memory_context = memory.search(
                f"data analysis {self.table_name} {self.column_name or 'all columns'}",
                user_id="system",
                category="query_patterns"
            )
            
            # Load data sample
            df = self._load_data_sample(engine)
            if df is None or len(df) == 0:
                return f"❌ Error: No data found in table '{self.table_name}'"
            
            # Perform analysis based on type
            if self.analysis_type == "summary":
                result = self._perform_summary_analysis(df)
            elif self.analysis_type == "detailed":
                result = self._perform_detailed_analysis(df)
            elif self.analysis_type == "correlation":
                result = self._perform_correlation_analysis(df)
            elif self.analysis_type == "distribution":
                result = self._perform_distribution_analysis(df)
            else:
                return f"❌ Error: Unknown analysis type '{self.analysis_type}'"
            
            # Generate insights and recommendations
            insights = self._generate_insights(df, result)
            
            # Store analysis results in memory
            self._store_analysis_in_memory(memory, result, insights)
            
            # Format final response
            formatted_response = self._format_analysis_response(result, insights, memory_context)
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Data analysis failed: {str(e)}"
            logger.error(error_msg)
            
            memory = self.agent.get_memory_instance()
            memory.add(
                error_msg,
                user_id="system",
                category="error_log",
                metadata={"error_type": "data_analysis_error", "tool": "DataAnalysisTool"}
            )
            
            return f"❌ **Data Analysis Error:**\n{str(e)}"
    
    def _load_data_sample(self, engine) -> Optional[pd.DataFrame]:
        """Load a representative sample of data from the specified table"""
        try:
            base_query = f"SELECT * FROM {self.table_name}"
            
            # Add column filtering if specified
            if self.column_name:
                base_query = f"SELECT {self.column_name} FROM {self.table_name}"
            
            # Add sampling for performance
            query = f"{base_query} ORDER BY RANDOM() LIMIT {self.sample_size}"
            
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                return df
                
        except Exception as e:
            logger.error(f"Failed to load data sample: {e}")
            return None
    
    def _perform_summary_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform basic summary statistics analysis"""
        result = {
            'analysis_type': 'summary',
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            result['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            result['categorical_summary'][col] = {
                'unique_count': df[col].nunique(),
                'most_frequent': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                'value_counts': df[col].value_counts().head(5).to_dict()
            }
        
        return result
    
    def _perform_detailed_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform detailed statistical analysis including outliers and patterns"""
        result = self._perform_summary_analysis(df)
        result['analysis_type'] = 'detailed'
        
        # Advanced analysis for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        result['advanced_numeric'] = {}
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outlier_threshold_low = Q1 - 1.5 * IQR
                outlier_threshold_high = Q3 + 1.5 * IQR
                
                outliers = col_data[(col_data < outlier_threshold_low) | 
                                  (col_data > outlier_threshold_high)]
                
                result['advanced_numeric'][col] = {
                    'outlier_count': len(outliers),
                    'outlier_percentage': (len(outliers) / len(col_data)) * 100,
                    'iqr': IQR,
                    'skewness': col_data.skew(),
                    'kurtosis': col_data.kurtosis()
                }
        
        # Pattern detection
        result['patterns'] = self._detect_patterns(df)
        
        return result
    
    def _perform_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform correlation analysis between numeric columns"""
        result = {'analysis_type': 'correlation'}
        
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            result['error'] = "Need at least 2 numeric columns for correlation analysis"
            return result
        
        # Calculate correlation matrix
        correlation_matrix = numeric_df.corr()
        result['correlation_matrix'] = correlation_matrix.to_dict()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(correlation_matrix.columns):
            for j, col2 in enumerate(correlation_matrix.columns):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': corr_value,
                            'strength': 'strong' if abs(corr_value) > 0.8 else 'moderate'
                        })
        
        result['strong_correlations'] = strong_correlations
        return result
    
    def _perform_distribution_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data distributions and identify patterns"""
        result = {'analysis_type': 'distribution'}
        
        # Analyze each column's distribution
        result['distributions'] = {}
        
        for col in df.columns:
            col_analysis = {'column_name': col, 'data_type': str(df[col].dtype)}
            
            if df[col].dtype in ['int64', 'float64']:
                # Numeric distribution analysis
                col_data = df[col].dropna()
                col_analysis.update({
                    'distribution_type': self._identify_distribution_type(col_data),
                    'histogram_bins': self._calculate_histogram_info(col_data),
                    'normality_test': self._test_normality(col_data)
                })
            else:
                # Categorical distribution analysis
                value_counts = df[col].value_counts()
                col_analysis.update({
                    'distribution_type': 'categorical',
                    'entropy': self._calculate_entropy(value_counts),
                    'concentration': self._calculate_concentration_ratio(value_counts)
                })
            
            result['distributions'][col] = col_analysis
        
        return result
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect common data patterns and anomalies"""
        patterns = {}
        
        # Check for potential ID columns
        for col in df.columns:
            if df[col].dtype in ['int64', 'object']:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio > 0.95:
                    patterns[f"{col}_likely_id"] = f"Column '{col}' appears to be an ID field (95%+ unique values)"
        
        # Check for potential timestamp columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Simple timestamp pattern detection
                sample_values = df[col].dropna().head(10).astype(str)
                timestamp_like = sum(1 for val in sample_values 
                                   if re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', val))
                if timestamp_like >= 7:  # 70% threshold
                    patterns[f"{col}_likely_timestamp"] = f"Column '{col}' appears to contain timestamp data"
        
        return patterns
    
    def _identify_distribution_type(self, data: pd.Series) -> str:
        """Identify the likely distribution type of numeric data"""
        if len(data) < 10:
            return "insufficient_data"
        
        # Simple heuristics for common distributions
        skewness = data.skew()
        kurtosis = data.kurtosis()
        
        if abs(skewness) < 0.5 and abs(kurtosis) < 3:
            return "approximately_normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 3:
            return "heavy_tailed"
        else:
            return "unknown"
    
    def _calculate_histogram_info(self, data: pd.Series) -> Dict[str, Any]:
        """Calculate histogram information for numeric data"""
        try:
            counts, bins = np.histogram(data, bins='auto')
            return {
                'bin_count': len(bins) - 1,
                'max_frequency': int(counts.max()),
                'min_frequency': int(counts.min())
            }
        except:
            return {'error': 'Failed to calculate histogram'}
    
    def _test_normality(self, data: pd.Series) -> Dict[str, Any]:
        """Simple normality test based on skewness and kurtosis"""
        skewness = data.skew()
        kurtosis = data.kurtosis()
        
        # Simple normality assessment
        is_normal = abs(skewness) < 0.5 and abs(kurtosis - 3) < 1
        
        return {
            'likely_normal': is_normal,
            'skewness': skewness,
            'excess_kurtosis': kurtosis - 3
        }
    
    def _calculate_entropy(self, value_counts: pd.Series) -> float:
        """Calculate Shannon entropy for categorical data"""
        try:
            probabilities = value_counts / value_counts.sum()
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            return entropy
        except:
            return 0.0
    
    def _calculate_concentration_ratio(self, value_counts: pd.Series) -> float:
        """Calculate how concentrated the data is in the top values"""
        try:
            total = value_counts.sum()
            top_5_sum = value_counts.head(5).sum()
            return (top_5_sum / total) if total > 0 else 0
        except:
            return 0.0
    
    def _generate_insights(self, df: pd.DataFrame, analysis_result: Dict) -> List[str]:
        """Generate actionable insights based on analysis results"""
        insights = []
        
        # Data quality insights
        missing_values = analysis_result.get('missing_values', {})
        total_cells = len(df) * len(df.columns)
        total_missing = sum(missing_values.values())
        
        if total_missing > 0:
            missing_percentage = (total_missing / total_cells) * 100
            insights.append(f"Data quality concern: {missing_percentage:.1f}% of data is missing")
        
        # Performance insights
        if analysis_result.get('memory_usage', 0) > 100_000_000:  # 100MB
            insights.append("Performance insight: Dataset is large, consider indexing or partitioning")
        
        # Column-specific insights
        for col, summary in analysis_result.get('categorical_summary', {}).items():
            unique_ratio = summary['unique_count'] / len(df)
            if unique_ratio > 0.9:
                insights.append(f"Column '{col}' has very high cardinality - consider normalization")
        
        # Correlation insights
        if 'strong_correlations' in analysis_result:
            for corr in analysis_result['strong_correlations']:
                insights.append(f"Strong correlation found: {corr['column1']} ↔ {corr['column2']} (r={corr['correlation']:.3f})")
        
        return insights
    
    def _store_analysis_in_memory(self, memory, analysis_result: Dict, insights: List[str]):
        """Store analysis results in memory for future reference"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Store main analysis summary
            summary = f"Data analysis of {self.table_name}: {analysis_result.get('row_count', 0)} rows, "
            summary += f"{analysis_result.get('column_count', 0)} columns. Analysis type: {analysis_result.get('analysis_type', 'unknown')}"
            
            memory.add(
                summary,
                user_id="system",
                category="query_patterns",
                metadata={
                    "table_name": self.table_name,
                    "analysis_type": self.analysis_type,
                    "timestamp": timestamp,
                    "row_count": analysis_result.get('row_count', 0)
                }
            )
            
            # Store key insights
            for insight in insights:
                memory.add(
                    f"Data insight for {self.table_name}: {insight}",
                    user_id="system",
                    category="performance_insights",
                    metadata={"table_name": self.table_name, "insight_type": "data_analysis"}
                )
                
        except Exception as e:
            logger.error(f"Failed to store analysis in memory: {e}")
    
    def _format_analysis_response(self, analysis_result: Dict, insights: List[str], 
                                memory_context: List[Dict]) -> str:
        """Format the complete analysis response"""
        response = f"📊 **Data Analysis Report: {self.table_name}**\n\n"
        
        # Basic information
        response += f"🔍 **Analysis Type:** {analysis_result.get('analysis_type', 'unknown').title()}\n"
        response += f"📏 **Dataset Size:** {analysis_result.get('row_count', 'N/A')} rows, {analysis_result.get('column_count', 'N/A')} columns\n\n"
        
        # Memory usage
        if 'memory_usage' in analysis_result:
            mb_size = analysis_result['memory_usage'] / (1024 * 1024)
            response += f"💾 **Memory Usage:** {mb_size:.2f} MB\n\n"
        
        # Missing values summary
        if 'missing_values' in analysis_result:
            missing = analysis_result['missing_values']
            if any(v > 0 for v in missing.values()):
                response += "⚠️ **Missing Values:**\n"
                for col, count in missing.items():
                    if count > 0:
                        percentage = (count / analysis_result.get('row_count', 1)) * 100
                        response += f"   - {col}: {count} ({percentage:.1f}%)\n"
                response += "\n"
        
        # Numeric summary
        if 'numeric_summary' in analysis_result and analysis_result['numeric_summary']:
            response += "📈 **Numeric Columns Summary:**\n"
            for col, stats in analysis_result['numeric_summary'].items():
                response += f"   **{col}:**\n"
                response += f"     - Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}\n"
                response += f"     - Range: {stats['min']:.2f} to {stats['max']:.2f}\n"
            response += "\n"
        
        # Categorical summary
        if 'categorical_summary' in analysis_result and analysis_result['categorical_summary']:
            response += "🏷️ **Categorical Columns Summary:**\n"
            for col, stats in analysis_result['categorical_summary'].items():
                response += f"   **{col}:** {stats['unique_count']} unique values\n"
                if 'most_frequent' in stats and stats['most_frequent']:
                    response += f"     - Most frequent: {stats['most_frequent']}\n"
            response += "\n"
        
        # Strong correlations
        if 'strong_correlations' in analysis_result:
            correlations = analysis_result['strong_correlations']
            if correlations:
                response += "🔗 **Strong Correlations Found:**\n"
                for corr in correlations:
                    response += f"   - {corr['column1']} ↔ {corr['column2']}: {corr['correlation']:.3f} ({corr['strength']})\n"
                response += "\n"
        
        # Insights and recommendations
        if insights:
            response += "💡 **Key Insights & Recommendations:**\n"
            for i, insight in enumerate(insights, 1):
                response += f"   {i}. {insight}\n"
            response += "\n"
        
        # Previous analysis context
        if memory_context:
            response += "🧠 **Previous Analysis Context:**\n"
            for context in memory_context[:2]:  # Show top 2 relevant memories
                response += f"   - {context['memory'][:100]}...\n"
        
        return response


if __name__ == "__main__":
    print("DataAnalysisTool - Use within DatabaseAnalysisAgent context")