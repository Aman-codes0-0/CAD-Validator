import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

class ReportGenerator:
    def __init__(self, filename, output_dir="."):
        self.filename = os.path.basename(filename)
        self.output_path = os.path.join(output_dir, f"report_{self.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
    def generate(self, features, rule_results, ml_result, suggestions):
        doc = SimpleDocTemplate(self.output_path, pagesize=A4, rightMargin=72,leftMargin=72, topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=TA_CENTER, textColor=colors.darkblue)
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        Story = []
        
        # 1. Header
        Story.append(Paragraph("AI-Driven CAD Validation Report", title_style))
        Story.append(Spacer(1, 12))
        Story.append(Paragraph(f"<b>File:</b> {self.filename}", normal_style))
        Story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        Story.append(Spacer(1, 24))
        
        # 2. Overall Verdict (ML Result)
        Story.append(Paragraph("1. Overall AI Verdict", heading_style))
        verdict_color = colors.green if ml_result['verdict'] == 'PASS' else colors.red
        verdict_text = f"<font color={verdict_color.hexval()}><b>{ml_result['verdict']}</b></font> (Confidence: {ml_result['confidence']}%)"
        Story.append(Paragraph(verdict_text, normal_style))
        Story.append(Spacer(1, 24))
        
        # 3. Geometric Features Table
        Story.append(Paragraph("2. Extracted Features", heading_style))
        feat_data = [["Feature", "Value"]]
        for k, v in features.items():
            feat_data.append([k.replace('_', ' ').title(), str(v)])
            
        t = Table(feat_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        Story.append(t)
        Story.append(Spacer(1, 24))
        
        # 4. Rule Violations
        Story.append(Paragraph("3. Rule Violations & Warnings", heading_style))
        if rule_results:
            rule_data = [["Attribute", "Severity", "Message"]]
            for r in rule_results:
                sev_color = colors.red if r['severity'] == "ERROR" else (colors.orange if r['severity'] == "WARNING" else colors.green)
                rule_data.append([r['rule'], r['severity'], r['message']])
                
            t_r = Table(rule_data, colWidths=[100, 70, 230])
            t_r.setStyle(TableStyle([
                 ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                 ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                 ('GRID', (0,0), (-1,-1), 1, colors.black),
                 ('VALIGN', (0,0), (-1,-1), 'TOP')
            ]))
            Story.append(t_r)
        else:
            Story.append(Paragraph("No rule violations found.", normal_style))
            
        Story.append(Spacer(1, 24))
        
        # 5. Suggestions
        Story.append(Paragraph("4. AI Suggestions for Improvement", heading_style))
        if suggestions:
            for s in suggestions:
                Story.append(Paragraph(f"• <b>{s['title']}</b>: {s['desc']}", normal_style))
                Story.append(Spacer(1, 6))
        else:
            Story.append(Paragraph("Design is optimal. No changes suggested.", normal_style))
            
        doc.build(Story)
        return self.output_path
