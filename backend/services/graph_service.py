import numpy as np
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64

class GraphService:
    def __init__(self):
        pass

    def process_chart_data(self, data):
        """
        Process raw data for charts. 
        Expects labels (comma-sep) and values (comma-sep).
        In a real app, this could involve statistical analysis, 
        trend prediction, or fetching from a database.
        """
        raw_labels = data.get('labels', '')
        raw_values = data.get('values', '')
        chart_type = data.get('type', 'bar')
        
        # Simple cleanup
        labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        try:
            values = [float(v.strip()) for v in raw_values.split(',') if v.strip()]
        except ValueError:
            values = []

        # Ensure labels and values match length
        max_len = max(len(labels), len(values))
        labels = (labels + ["Label"] * max_len)[:max_len]
        values = (values + [0] * max_len)[:max_len]

        # Backend Logic: Calculate simple stats
        stats = {
            'sum': sum(values),
            'avg': sum(values) / len(values) if values else 0,
            'max': max(values) if values else 0,
            'min': min(values) if values else 0
        }

        # Return data optimized for Chart.js
        return {
            'labels': labels,
            'datasets': [{
                'label': data.get('title', 'Dataset'),
                'data': values,
                'backgroundColor': self._get_colors(chart_type, len(values)),
                'borderColor': '#0d9488', # Vibrant Teal
                'borderWidth': 1
            }],
            'stats': stats
        }

    def generate_matplotlib_plot(self, data):
        """
        Generate a graph using Matplotlib and return as base64 string.
        """
        raw_labels = data.get('labels', '')
        raw_values = data.get('values', '')
        chart_type = data.get('type', 'bar')
        title = data.get('title', 'Data Plot')
        
        labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        try:
            values = [float(v.strip()) for v in raw_values.split(',') if v.strip()]
        except ValueError:
            values = []

        # Ensure matching length
        max_len = max(len(labels), len(values))
        labels = (labels + [""] * (max_len - len(labels))) if len(labels) < max_len else labels
        values = (values + [0] * (max_len - len(values))) if len(values) < max_len else values

        plt.figure(figsize=(10, 6))
        
        # Consistent Teal Theme
        color = '#0d9488' # StudioFlow Teal
        
        if chart_type == 'line':
            plt.plot(labels, values, marker='o', color=color, linewidth=2, markersize=8)
            plt.fill_between(labels, values, alpha=0.1, color=color)
        elif chart_type == 'pie':
            plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#0d9488', '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4'])
        else: # bar
            plt.bar(labels, values, color=color, alpha=0.8)

        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close() # Clean up
        
        return {
            'image': f'data:image/png;base64,{img_str}',
            'stats': {
                'sum': sum(values),
                'avg': sum(values) / len(values) if values else 0,
                'max': max(values) if values else 0,
                'min': min(values) if values else 0
            }
        }

    def _get_colors(self, chart_type, count):
        # Professional teal palette
        colors = [
            'rgba(13, 148, 136, 0.7)',  # vibrant teal
            'rgba(110, 231, 183, 0.7)', # mint accent
            'rgba(51, 65, 85, 0.7)',    # charcoal
            'rgba(204, 251, 241, 0.7)', # light teal
            'rgba(15, 118, 110, 0.7)',  # dark teal
        ]
        if chart_type == 'pie':
            # Cycle through colors if count > len(colors)
            return [colors[i % len(colors)] for i in range(count)]
        return colors[0] # Single color for bars/lines
