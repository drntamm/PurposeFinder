from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///purpose_finder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Handle Render's PostgreSQL URL format
if app.config['SQLALCHEMY_DATABASE_URI'] and app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)

# Database Models
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    love_answers = db.Column(db.JSON)
    skill_answers = db.Column(db.JSON)
    world_needs_answers = db.Column(db.JSON)
    career_answers = db.Column(db.JSON)
    spiritual_gifts_answers = db.Column(db.JSON)
    results = db.Column(db.JSON)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    data = request.json
    
    # Create new assessment
    assessment = Assessment(
        love_answers=data.get('love_answers'),
        skill_answers=data.get('skill_answers'),
        world_needs_answers=data.get('world_needs_answers'),
        spiritual_gifts_answers=data.get('spiritual_gifts_answers')
    )
    
    # Analyze results
    results = analyze_results(data)
    assessment.results = results
    
    db.session.add(assessment)
    db.session.commit()
    
    return jsonify({'id': assessment.id, 'results': results})

@app.route('/results')
def results():
    assessment_id = request.args.get('id')
    if not assessment_id:
        return redirect(url_for('assessment'))
    
    assessment = Assessment.query.get_or_404(assessment_id)
    return render_template('results.html', results=assessment.results)

def analyze_results(data):
    # Extract keywords from responses
    love_keywords = extract_keywords(data['love_answers'])
    skill_keywords = extract_keywords(data['skill_answers'])
    world_needs_keywords = extract_keywords(data['world_needs_answers'])
    spiritual_keywords = extract_keywords(data['spiritual_gifts_answers'])
    
    # Map spiritual keywords to gifts
    spiritual_gifts = analyze_spiritual_gifts(spiritual_keywords)
    
    # Generate career suggestions based on combined keywords
    careers = suggest_careers(love_keywords + skill_keywords + world_needs_keywords)
    
    # Generate recommendations
    recommendations = generate_recommendations(love_keywords, skill_keywords, world_needs_keywords, spiritual_gifts)
    
    return {
        'spiritual_gifts': spiritual_gifts,
        'ikigai': {
            'love': list(love_keywords),
            'skill': list(skill_keywords),
            'world_needs': list(world_needs_keywords),
            'career': careers
        },
        'recommendations': recommendations
    }

def extract_keywords(answers):
    if not answers:
        return set()
    
    # Combine all answers into a single string
    text = ' '.join(str(value) for value in answers.values())
    
    # Simple keyword extraction (you might want to use NLTK or spaCy for better results)
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    return {word for word in words if len(word) > 3 and word not in stopwords}

def analyze_spiritual_gifts(keywords):
    # Map keywords to spiritual gifts
    gift_mapping = {
        'teach': {'name': 'Teaching', 'description': 'You have a gift for explaining and helping others understand complex concepts.'},
        'help': {'name': 'Helping', 'description': 'You find joy in serving others and meeting practical needs.'},
        'lead': {'name': 'Leadership', 'description': 'You have a natural ability to guide and inspire others.'},
        'encourage': {'name': 'Encouragement', 'description': 'You excel at supporting and uplifting others.'},
        'give': {'name': 'Giving', 'description': 'You are generous with your resources and find fulfillment in supporting causes.'},
        'mercy': {'name': 'Mercy', 'description': 'You have deep empathy and compassion for those who are suffering.'},
        'wisdom': {'name': 'Wisdom', 'description': 'You have insight into making good decisions and giving sound advice.'},
    }
    
    gifts = []
    for keyword in keywords:
        for gift_key, gift_info in gift_mapping.items():
            if gift_key in keyword:
                gifts.append(gift_info)
    
    # Add default gift if none found
    if not gifts:
        gifts.append({
            'name': 'Service',
            'description': 'You have a general calling to serve others and make a positive impact.'
        })
    
    return gifts

def suggest_careers(keywords):
    # Simple career mapping based on keywords
    career_mapping = {
        'teach': ['Teacher', 'Trainer', 'Coach'],
        'write': ['Writer', 'Content Creator', 'Journalist'],
        'help': ['Counselor', 'Social Worker', 'Healthcare Professional'],
        'create': ['Artist', 'Designer', 'Developer'],
        'lead': ['Manager', 'Entrepreneur', 'Community Leader'],
        'analyze': ['Researcher', 'Analyst', 'Consultant'],
        'care': ['Healthcare Provider', 'Therapist', 'Caregiver'],
    }
    
    careers = set()
    for keyword in keywords:
        for career_key, career_list in career_mapping.items():
            if career_key in keyword:
                careers.update(career_list)
    
    return list(careers) if careers else ['Consider exploring careers that combine your interests with opportunities to serve others']

def generate_recommendations(love_keywords, skill_keywords, world_needs_keywords, spiritual_gifts):
    recommendations = []
    
    # Combine interests and skills
    if love_keywords and skill_keywords:
        recommendations.append(
            f"Consider ways to combine your interests in {', '.join(list(love_keywords)[:3])} "
            f"with your skills in {', '.join(list(skill_keywords)[:3])}."
        )
    
    # Add spiritual gift recommendation
    if spiritual_gifts:
        recommendations.append(
            f"Your spiritual gift of {spiritual_gifts[0]['name']} suggests you could make a significant "
            f"impact through {spiritual_gifts[0]['description'].lower()}"
        )
    
    # Add world impact recommendation
    if world_needs_keywords:
        recommendations.append(
            f"Your concern for {', '.join(list(world_needs_keywords)[:3])} could be channeled into "
            f"meaningful volunteer work or career opportunities."
        )
    
    return recommendations

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
