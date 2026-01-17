"""
CSV Import/Export Service
Handles CSV file processing for database blocks
"""
import pandas as pd
import io
import json
from typing import List, Dict, Any


class CSVService:
    
    def import_csv(self, file_content: bytes, has_header: bool = True) -> Dict[str, Any]:
        """
        Import CSV file and convert to database block format
        
        Args:
            file_content: CSV file bytes
            has_header: Whether first row is header
            
        Returns:
            Dictionary with columns and rows
        """
        try:
            # Read CSV
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Get column names
            columns = df.columns.tolist()
            
            # Convert to list of dictionaries
            rows = df.to_dict('records')
            
            # Clean NaN values
            for row in rows:
                for key in row:
                    if pd.isna(row[key]):
                        row[key] = ''
            
            return {
                'success': True,
                'columns': columns,
                'rows': rows,
                'rowCount': len(rows),
                'columnCount': len(columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_csv(self, data: Dict[str, Any]) -> bytes:
        """
        Export database block to CSV
        
        Args:
            data: Dictionary with 'columns' and 'rows'
            
        Returns:
            CSV file bytes
        """
        try:
            columns = data.get('columns', [])
            rows = data.get('rows', [])
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            return csv_buffer.getvalue().encode('utf-8')
            
        except Exception as e:
            raise Exception(f'CSV export failed: {e}')
    
    def validate_csv(self, file_content: bytes) -> Dict[str, Any]:
        """
        Validate CSV file structure
        
        Returns:
            Validation result with preview
        """
        try:
            df = pd.read_csv(io.BytesIO(file_content), nrows=5)
            
            return {
                'valid': True,
                'columns': df.columns.tolist(),
                'preview': df.to_dict('records'),
                'estimatedRows': len(pd.read_csv(io.BytesIO(file_content)))
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
