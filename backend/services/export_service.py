from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
import base64
from PIL import Image

class ExportService:
    """Service for exporting documents and canvas to various formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomH1',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=12,
            textColor='#1a1a24'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomH2',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=10,
            textColor='#1a1a24'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomH3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor='#1a1a24'
        ))
    
    def export_to_pdf(self, content, title='Document'):
        """
        Export document content to PDF
        
        Args:
            content: Dictionary with 'blocks' array
            title: Document title
        
        Returns:
            bytes: PDF file content
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Title'],
            fontSize=28,
            textColor='#8b5cf6',
            spaceAfter=20,
            alignment=TA_CENTER
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Process blocks
        blocks = content.get('blocks', [])
        
        for block in blocks:
            block_type = block.get('type', 'p')
            text = block.get('text', '').strip()
            
            # Handle Graph/Image Blocks
            if block_type == 'graph':
                img_data = block.get('content', '')
                if img_data:
                    try:
                        # Clean base64 string
                        if 'base64,' in img_data:
                            img_data = img_data.split('base64,')[1]
                        
                        img_bytes = base64.b64decode(img_data)
                        img_buffer = BytesIO(img_bytes)
                        img = Image.open(img_buffer)
                        
                        # Resize to fit width if needed (max 450 pt wide approx)
                        width, height = img.size
                        aspect = height / float(width)
                        display_width = 450
                        display_height = display_width * aspect
                        
                        from reportlab.platypus import Image as RLImage
                        # Re-open buffer for ReportLab
                        img_buffer.seek(0)
                        rl_img = RLImage(img_buffer, width=display_width, height=display_height)
                        story.append(rl_img)
                        story.append(Spacer(1, 0.2 * inch))
                    except Exception as e:
                        print(f"Error processing image: {e}")
                continue

            if not text:
                continue
            
            # Clean HTML tags from text
            text = self._clean_html(text)
            
            if block_type == 'h1':
                story.append(Paragraph(text, self.styles['CustomH1']))
            elif block_type == 'h2':
                story.append(Paragraph(text, self.styles['CustomH2']))
            elif block_type == 'h3':
                story.append(Paragraph(text, self.styles['CustomH3']))
            else:
                story.append(Paragraph(text, self.styles['BodyText']))
            
            story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def export_to_markdown(self, content):
        """
        Export document content to Markdown
        
        Args:
            content: Dictionary with 'blocks' array
        
        Returns:
            str: Markdown formatted text
        """
        markdown = []
        blocks = content.get('blocks', [])
        
        for block in blocks:
            block_type = block.get('type', 'p')
            text = block.get('text', '').strip()
            
            if not text:
                continue
            
            # Clean HTML tags
            text = self._clean_html(text)
            
            if block_type == 'h1':
                markdown.append(f'# {text}\n')
            elif block_type == 'h2':
                markdown.append(f'## {text}\n')
            elif block_type == 'h3':
                markdown.append(f'### {text}\n')
            else:
                markdown.append(f'{text}\n')
            
            markdown.append('\n')
        
        return ''.join(markdown)
    
    def export_to_html(self, content, title='Document'):
        """
        Export document content to HTML
        
        Args:
            content: Dictionary with 'blocks' array
            title: Document title
        
        Returns:
            str: HTML formatted text
        """
        html = [f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f9fafb;
            color: #1a1a24;
            line-height: 1.6;
        }}
        h1 {{
            color: #8b5cf6;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        h2 {{
            color: #1a1a24;
            font-size: 2rem;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }}
        h3 {{
            color: #1a1a24;
            font-size: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        p {{
            margin-bottom: 1rem;
        }}
        ul, ol {{
            margin-bottom: 1rem;
            padding-left: 2rem;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
''']
        
        blocks = content.get('blocks', [])
        
        for block in blocks:
            block_type = block.get('type', 'p')
            content_html = block.get('content', '')
            
            if not content_html.strip():
                continue
            
            if block_type == 'h1':
                html.append(f'    <h1>{content_html}</h1>\n')
            elif block_type == 'h2':
                html.append(f'    <h2>{content_html}</h2>\n')
            elif block_type == 'h3':
                html.append(f'    <h3>{content_html}</h3>\n')
            else:
                html.append(f'    <p>{content_html}</p>\n')
        
        html.append('''</body>
</html>''')
        
        return ''.join(html)
    
    def export_canvas_to_png(self, canvas_data):
        """
        Export canvas to PNG image
        
        Args:
            canvas_data: Base64 encoded image data
        
        Returns:
            bytes: PNG image content
        """
        try:
            # Remove data URL prefix if present
            if ',' in canvas_data:
                canvas_data = canvas_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(canvas_data)
            
            # Open with PIL and save as PNG
            image = Image.open(BytesIO(image_bytes))
            
            output = BytesIO()
            image.save(output, format='PNG')
            
            png_bytes = output.getvalue()
            output.close()
            
            return png_bytes
        
        except Exception as e:
            raise Exception(f'Failed to export canvas: {str(e)}')
    
    def _clean_html(self, text):
        """Remove HTML tags from text"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        return text.strip()
