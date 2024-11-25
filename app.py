from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from datetime import datetime
import re
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this')

# Database Configuration
database_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///purpose_finder.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Form Class
class AssessmentForm(FlaskForm):
    love_activities = TextAreaField('What activities do you love doing?', validators=[DataRequired()])
    love_topics = TextAreaField('What topics interest you the most?', validators=[DataRequired()])
    skills_natural = TextAreaField('What are your natural skills?', validators=[DataRequired()])
    skills_compliments = TextAreaField('What do people compliment you on?', validators=[DataRequired()])
    world_problems = TextAreaField('What problems do you want to solve?', validators=[DataRequired()])
    world_impact = TextAreaField('How do you want to impact the world?', validators=[DataRequired()])
    spiritual_service = TextAreaField('How do you like to serve others?', validators=[DataRequired()])
    spiritual_fulfillment = TextAreaField('What brings you spiritual fulfillment?', validators=[DataRequired()])

# Database Models
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    love_activities = db.Column(db.Text)
    love_topics = db.Column(db.Text)
    skills_natural = db.Column(db.Text)
    skills_compliments = db.Column(db.Text)
    world_problems = db.Column(db.Text)
    world_impact = db.Column(db.Text)
    spiritual_service = db.Column(db.Text)
    spiritual_fulfillment = db.Column(db.Text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    form = AssessmentForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create new assessment
            assessment = Assessment(
                love_activities=form.love_activities.data,
                love_topics=form.love_topics.data,
                skills_natural=form.skills_natural.data,
                skills_compliments=form.skills_compliments.data,
                world_problems=form.world_problems.data,
                world_impact=form.world_impact.data,
                spiritual_service=form.spiritual_service.data,
                spiritual_fulfillment=form.spiritual_fulfillment.data
            )
            
            # Save to database
            db.session.add(assessment)
            db.session.commit()
            
            # Process results
            results = analyze_assessment(assessment)
            
            return render_template('results.html', results=results)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving assessment: {str(e)}')
            return render_template('assessment.html', form=form)
    
    return render_template('assessment.html', form=form)

def analyze_assessment(assessment):
    # Extract keywords from responses
    keywords = []
    for field in [assessment.love_activities, assessment.love_topics, 
                 assessment.skills_natural, assessment.skills_compliments,
                 assessment.world_problems, assessment.world_impact,
                 assessment.spiritual_service, assessment.spiritual_fulfillment]:
        if field:
            # Split text into words and clean them
            words = re.findall(r'\w+', field.lower())
            keywords.extend(words)
    
    # Basic spiritual gifts mapping
    spiritual_gifts = {
        'teaching': ['teach', 'explain', 'educate', 'mentor', 'guide'],
        'service': ['help', 'serve', 'support', 'assist', 'volunteer'],
        'leadership': ['lead', 'direct', 'organize', 'manage', 'coordinate'],
        'mercy': ['care', 'comfort', 'empathize', 'counsel', 'listen'],
        'giving': ['share', 'provide', 'donate', 'contribute', 'give'],
        'encouragement': ['encourage', 'motivate', 'inspire', 'uplift', 'strengthen'],
        'wisdom': ['advise', 'counsel', 'guide', 'discern', 'understand']
    }
    
    # Find matching spiritual gifts
    matched_gifts = []
    for gift, indicators in spiritual_gifts.items():
        if any(indicator in keywords for indicator in indicators):
            matched_gifts.append(gift)
    
    # Career suggestions based on keywords
    careers = []
    if any(word in keywords for word in ['teach', 'educate', 'mentor']):
        careers.append('Teacher/Educator')
    if any(word in keywords for word in ['help', 'counsel', 'care']):
        careers.append('Counselor/Therapist')
    if any(word in keywords for word in ['lead', 'manage', 'organize']):
        careers.append('Ministry Leader')
    if any(word in keywords for word in ['create', 'design', 'build']):
        careers.append('Creative Professional')
    
    # Generate recommendations
    recommendations = []
    if matched_gifts:
        recommendations.append(f"Your spiritual gifts of {', '.join(matched_gifts)} suggest you would excel in roles that involve {', '.join(careers)}.")
    if 'teach' in keywords or 'mentor' in keywords:
        recommendations.append("Consider pursuing opportunities to teach or mentor others in your areas of expertise.")
    if 'help' in keywords or 'serve' in keywords:
        recommendations.append("Look for ways to serve your community through volunteer work or ministry.")
    
    return {
        'spiritual_gifts': matched_gifts,
        'careers': careers,
        'recommendations': recommendations
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
