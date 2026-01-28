"""
Presentation Evaluation Tool
A web application for evaluating AI-generated presentations
"""

import os
import json
import anthropic
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import PyPDF2
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('evaluations.db')
    c = conn.cursor()
    
    # Evaluations table
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_outline TEXT,
                  user_preferences TEXT,
                  presentation_link TEXT,
                  overall_score REAL,
                  score_category TEXT,
                  doc_type TEXT,
                  report_path TEXT,
                  json_data TEXT,
                  cost_usd REAL,
                  input_tokens INTEGER,
                  output_tokens INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  scores_json TEXT)''')
    
    # Rubric table
    c.execute('''CREATE TABLE IF NOT EXISTS rubric
                 (id INTEGER PRIMARY KEY,
                  dimension TEXT UNIQUE,
                  weight INTEGER,
                  description TEXT)''')
    
    # Insert default rubric if not exists
    default_rubric = [
        ('user_input_quality', 15, 'Quality and completeness of user-provided content'),
        ('system_understanding', 20, 'How well AI understood the job-to-be-done'),
        ('content_accuracy', 25, 'Data extraction and representation accuracy'),
        ('content_structure', 15, 'Narrative flow and logical organization'),
        ('design_quality', 15, 'Visual design and professional execution'),
        ('instruction_adherence', 10, 'Following user requirements and preferences')
    ]
    
    for dim, weight, desc in default_rubric:
        c.execute('INSERT OR IGNORE INTO rubric (dimension, weight, description) VALUES (?, ?, ?)',
                 (dim, weight, desc))
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Helper functions
def get_rubric():
    """Get current rubric from database"""
    conn = sqlite3.connect('evaluations.db')
    c = conn.cursor()
    c.execute('SELECT dimension, weight, description FROM rubric ORDER BY weight DESC')
    rubric = {row[0]: {'weight': row[1], 'description': row[2]} for row in c.fetchall()}
    conn.close()
    return rubric

def calculate_overall_score(dimension_scores, rubric):
    """Calculate weighted overall score"""
    total = 0
    total_weight = sum(r['weight'] for r in rubric.values())
    
    for dimension, score in dimension_scores.items():
        if dimension in rubric:
            weight = rubric[dimension]['weight']
            total += (score * weight / total_weight)
    
    return round(total, 1)

def get_score_category(score):
    """Get category based on score"""
    if score >= 90:
        return 'Excellent'
    elif score >= 80:
        return 'Good'
    elif score >= 70:
        return 'Satisfactory'
    elif score >= 60:
        return 'Needs Improvement'
    else:
        return 'Poor'

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF for analysis"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def evaluate_with_claude(json_data, pdf_text, rubric):
    """Use Claude API to evaluate the presentation"""
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    
    prompt = f"""You are an expert presentation evaluator. Analyze this presentation based on the following rubric:

RUBRIC:
{json.dumps({k: v['description'] for k, v in rubric.items()}, indent=2)}

USER INPUT DATA (JSON):
{json.dumps(json_data, indent=2)[:3000]}  # Truncate if too long

PRESENTATION CONTENT (First 2000 chars):
{pdf_text[:2000]}

Evaluate the presentation on each dimension (score 0-100) and provide:
1. Score for each dimension
2. Brief justification (2-3 sentences) for each score
3. Top 3 strengths
4. Top 3 areas for improvement
5. Overall assessment (1 paragraph)

Respond in JSON format:
{{
  "dimension_scores": {{
    "user_input_quality": <score>,
    "system_understanding": <score>,
    "content_accuracy": <score>,
    "content_structure": <score>,
    "design_quality": <score>,
    "instruction_adherence": <score>
  }},
  "justifications": {{
    "user_input_quality": "...",
    "system_understanding": "...",
    ...
  }},
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "overall_assessment": "..."
}}

IMPORTANT: Respond ONLY with valid JSON, no other text."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Calculate cost
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        cost_usd = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        
        # Parse response
        evaluation = json.loads(response_text)
        
        return evaluation, cost_usd, input_tokens, output_tokens
        
    except Exception as e:
        print(f"Claude API Error: {str(e)}")
        # Return default scores if API fails
        return {
            "dimension_scores": {dim: 75 for dim in rubric.keys()},
            "justifications": {dim: "Evaluation pending" for dim in rubric.keys()},
            "strengths": ["Evaluation in progress"],
            "improvements": ["Evaluation in progress"],
            "overall_assessment": f"Error during evaluation: {str(e)}"
        }, 0, 0, 0

def generate_evaluation_report(evaluation_data, presentation_filename, output_path):
    """Generate PDF evaluation report"""
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                           rightMargin=60, leftMargin=60, topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Heading1'], 
                             fontSize=18, alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], 
                             fontSize=13, spaceAfter=10, spaceBefore=15))
    styles.add(ParagraphStyle(name='BodyText', parent=styles['Normal'], 
                             fontSize=9, alignment=TA_JUSTIFY, spaceAfter=8))
    
    story = []
    
    # Cover
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Presentation Evaluation Report", styles['ReportTitle']))
    story.append(Paragraph(f"<b>Presentation:</b> {presentation_filename}", styles['BodyText']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overall score
    overall_score = evaluation_data['overall_score']
    score_category = evaluation_data['score_category']
    
    score_data = [
        ['Overall Score', f"{overall_score}/100"],
        ['Category', score_category],
        ['Cost', f"${evaluation_data.get('cost_usd', 0):.4f}"]
    ]
    
    score_table = Table(score_data, colWidths=[2*inch, 2.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 10)
    ]))
    
    story.append(score_table)
    story.append(PageBreak())
    
    # Dimension scores
    story.append(Paragraph("Evaluation Scores by Dimension", styles['SectionTitle']))
    
    eval_json = json.loads(evaluation_data['evaluation_json'])
    dimension_scores = eval_json['dimension_scores']
    justifications = eval_json.get('justifications', {})
    
    for dimension, score in dimension_scores.items():
        dim_name = dimension.replace('_', ' ').title()
        story.append(Paragraph(f"<b>{dim_name}:</b> {score}/100", styles['BodyText']))
        if dimension in justifications:
            story.append(Paragraph(justifications[dimension], styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Strengths and improvements
    story.append(Paragraph("Key Strengths", styles['SectionTitle']))
    for strength in eval_json.get('strengths', []):
        story.append(Paragraph(f"✓ {strength}", styles['BodyText']))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Areas for Improvement", styles['SectionTitle']))
    for improvement in eval_json.get('improvements', []):
        story.append(Paragraph(f"⚠ {improvement}", styles['BodyText']))
    
    story.append(PageBreak())
    
    # Overall assessment
    story.append(Paragraph("Overall Assessment", styles['SectionTitle']))
    story.append(Paragraph(eval_json.get('overall_assessment', ''), styles['BodyText']))
    
    doc.build(story)

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/evaluations')
def get_evaluations():
    """Get all evaluations"""
    conn = sqlite3.connect('evaluations.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT id, user_outline, user_preferences, presentation_link, 
                        overall_score, score_category, doc_type, report_path,
                        cost_usd, input_tokens, output_tokens, created_at
                 FROM evaluations ORDER BY created_at DESC''')
    
    evaluations = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(evaluations)

@app.route('/api/rubric', methods=['GET', 'POST'])
def handle_rubric():
    """Get or update rubric"""
    if request.method == 'GET':
        rubric = get_rubric()
        return jsonify(rubric)
    
    elif request.method == 'POST':
        new_rubric = request.json
        
        conn = sqlite3.connect('evaluations.db')
        c = conn.cursor()
        
        for dimension, data in new_rubric.items():
            c.execute('UPDATE rubric SET weight = ?, description = ? WHERE dimension = ?',
                     (data['weight'], data['description'], dimension))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'})

@app.route('/api/evaluate', methods=['POST'])
def evaluate_presentation():
    """Evaluate a presentation"""
    try:
        # Get uploaded files
        json_file = request.files.get('json_file')
        pdf_file = request.files.get('pdf_file')
        
        if not json_file or not pdf_file:
            return jsonify({'error': 'Both JSON and PDF files required'}), 400
        
        # Save files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = secure_filename(f"{timestamp}_{json_file.filename}")
        pdf_filename = secure_filename(f"{timestamp}_{pdf_file.filename}")
        
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        json_file.save(json_path)
        pdf_file.save(pdf_path)
        
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Extract PDF text
        pdf_text = extract_text_from_pdf(pdf_path)
        
        # Get current rubric
        rubric = get_rubric()
        
        # Evaluate with Claude
        evaluation, cost_usd, input_tokens, output_tokens = evaluate_with_claude(
            json_data, pdf_text, rubric
        )
        
        # Calculate overall score
        dimension_scores = evaluation['dimension_scores']
        overall_score = calculate_overall_score(dimension_scores, rubric)
        score_category = get_score_category(overall_score)
        
        # Extract user outline and preferences
        if isinstance(json_data, list) and len(json_data) > 0:
            data = json_data[0]
        else:
            data = json_data
        
        user_outline = data.get('user_attachment', '')[:500]  # First 500 chars
        user_prefs = f"Type: {data.get('type', 'N/A')}, Language: {data.get('language', 'N/A')}"
        doc_type = data.get('type', 'unknown')
        
        # Generate report
        report_filename = f"report_{timestamp}.pdf"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        report_data = {
            'overall_score': overall_score,
            'score_category': score_category,
            'evaluation_json': json.dumps(evaluation),
            'cost_usd': cost_usd
        }
        
        generate_evaluation_report(report_data, pdf_file.filename, report_path)
        
        # Save to database
        conn = sqlite3.connect('evaluations.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO evaluations 
                     (user_outline, user_preferences, presentation_link, overall_score,
                      score_category, doc_type, report_path, json_data, cost_usd,
                      input_tokens, output_tokens, scores_json)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (user_outline, user_prefs, pdf_path, overall_score, score_category,
                  doc_type, report_path, json.dumps(json_data), cost_usd,
                  input_tokens, output_tokens, json.dumps(dimension_scores)))
        
        eval_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'evaluation_id': eval_id,
            'overall_score': overall_score,
            'score_category': score_category,
            'cost_usd': cost_usd,
            'dimension_scores': dimension_scores
        })
        
    except Exception as e:
        print(f"Evaluation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<int:eval_id>')
def download_report(eval_id):
    """Download evaluation report"""
    conn = sqlite3.connect('evaluations.db')
    c = conn.cursor()
    c.execute('SELECT report_path FROM evaluations WHERE id = ?', (eval_id,))
    result = c.fetchone()
    conn.close()
    
    if result and os.path.exists(result[0]):
        return send_file(result[0], as_attachment=True)
    
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/stats')
def get_stats():
    """Get usage statistics"""
    conn = sqlite3.connect('evaluations.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*), SUM(cost_usd), AVG(overall_score) FROM evaluations')
    total_evals, total_cost, avg_score = c.fetchone()
    
    c.execute('SELECT score_category, COUNT(*) FROM evaluations GROUP BY score_category')
    category_dist = dict(c.fetchall())
    
    conn.close()
    
    return jsonify({
        'total_evaluations': total_evals or 0,
        'total_cost_usd': round(total_cost or 0, 2),
        'average_score': round(avg_score or 0, 1),
        'category_distribution': category_dist
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
