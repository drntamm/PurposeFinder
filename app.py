from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets
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
migrate = Migrate(app, db)

# Checkbox Field
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Assessment Options
LOVE_ACTIVITIES = [
    ('teaching', 'Teaching and sharing knowledge'),
    ('puzzles', 'Solving puzzles or challenges'),
    ('writing', 'Writing stories, articles, or poetry'),
    ('music', 'Playing or creating music'),
    ('volunteering', 'Volunteering for social causes'),
    ('design', 'Designing creative projects'),
    ('research', 'Researching or learning new topics'),
    ('outdoor', 'Engaging in outdoor adventures'),
    ('cooking', 'Cooking or baking for others'),
    ('meditation', 'Practicing meditation or yoga')
]

LOVE_TOPICS = [
    ('tech', 'Science and technology innovations'),
    ('environment', 'Environmental sustainability'),
    ('psychology', 'Human psychology and behavior'),
    ('spirituality', 'Spirituality and faith-based practices'),
    ('growth', 'Personal growth and self-improvement'),
    ('history', 'History and cultural studies'),
    ('education', 'Education and instructional design'),
    ('justice', 'Social justice and activism'),
    ('health', 'Health and wellness'),
    ('business', 'Business and entrepreneurship')
]

NATURAL_SKILLS = [
    ('thinking', 'Critical thinking and problem-solving'),
    ('communication', 'Communicating ideas clearly'),
    ('creativity', 'Creativity in arts or design'),
    ('networking', 'Building relationships and networking'),
    ('organization', 'Organization and time management'),
    ('writing', 'Writing and storytelling'),
    ('leadership', 'Leadership and team-building'),
    ('analytical', 'Analytical or mathematical reasoning'),
    ('teaching', 'Teaching or coaching'),
    ('empathy', 'Empathy and understanding')
]

COMPLIMENTS = [
    ('listening', 'Your ability to listen and empathize'),
    ('patience', 'Your patience and kindness'),
    ('explaining', 'Your talent in explaining complex topics simply'),
    ('dedication', 'Your dedication and hard work'),
    ('creativity', 'Your creativity and innovation'),
    ('positivity', 'Your sense of humor and positivity'),
    ('leadership', 'Your leadership and guidance'),
    ('expertise', 'Your technical or subject matter expertise'),
    ('problem_solving', 'Your problem-solving ability'),
    ('reliability', 'Your reliability and trustworthiness')
]

WORLD_PROBLEMS = [
    ('education', 'Access to quality education'),
    ('climate', 'Climate change and environmental protection'),
    ('poverty', 'Poverty and economic inequality'),
    ('healthcare', 'Healthcare accessibility'),
    ('mental_health', 'Mental health awareness'),
    ('technology', 'Technology for social good'),
    ('human_rights', 'Human rights and social justice'),
    ('diversity', 'Diversity and inclusion'),
    ('sustainability', 'Sustainable development'),
    ('community', 'Community-building and empowerment')
]

WORLD_IMPACT = [
    ('innovation', 'Developing innovative solutions'),
    ('education', 'Providing education and training'),
    ('sustainability', 'Building sustainable communities'),
    ('advocacy', 'Advocating for equal rights'),
    ('technology', 'Using technology for social change'),
    ('art', 'Inspiring through art and storytelling'),
    ('research', 'Conducting impactful research'),
    ('mentorship', 'Mentoring and guiding others'),
    ('policy', 'Creating positive policy changes'),
    ('empowerment', 'Empowering marginalized communities')
]

SPIRITUAL_SERVICE = [
    ('teaching', 'Teaching and mentoring'),
    ('volunteering', 'Volunteering for community services'),
    ('counseling', 'Providing emotional support'),
    ('leadership', 'Leading by example'),
    ('organizing', 'Organizing charitable events'),
    ('giving', 'Offering financial or material help'),
    ('workshops', 'Hosting training sessions'),
    ('advocacy', 'Advocating for social causes'),
    ('healing', 'Supporting mental and emotional healing'),
    ('inspiration', 'Inspiring personal growth')
]

SPIRITUAL_FULFILLMENT = [
    ('growth', 'Helping others reach their potential'),
    ('impact', 'Witnessing positive changes'),
    ('mindfulness', 'Practicing gratitude'),
    ('wisdom', 'Sharing knowledge'),
    ('causes', 'Contributing to meaningful causes'),
    ('community', 'Building strong relationships'),
    ('faith', 'Inspiring through spirituality'),
    ('nature', 'Connecting with environment'),
    ('creativity', 'Creating transformative art'),
    ('mission', 'Being part of a larger vision')
]

# Form Class
class AssessmentForm(FlaskForm):
    love_activities = MultiCheckboxField('What activities do you love doing?', 
                                       choices=LOVE_ACTIVITIES,
                                       validators=[DataRequired()])
    love_topics = MultiCheckboxField('What topics interest you the most?',
                                    choices=LOVE_TOPICS,
                                    validators=[DataRequired()])
    skills_natural = MultiCheckboxField('What are your natural skills?',
                                      choices=NATURAL_SKILLS,
                                      validators=[DataRequired()])
    skills_compliments = MultiCheckboxField('What do people compliment you on?',
                                          choices=COMPLIMENTS,
                                          validators=[DataRequired()])
    world_problems = MultiCheckboxField('What problems do you want to solve?',
                                      choices=WORLD_PROBLEMS,
                                      validators=[DataRequired()])
    world_impact = MultiCheckboxField('How do you want to impact the world?',
                                    choices=WORLD_IMPACT,
                                    validators=[DataRequired()])
    spiritual_service = MultiCheckboxField('How do you like to serve others?',
                                         choices=SPIRITUAL_SERVICE,
                                         validators=[DataRequired()])
    spiritual_fulfillment = MultiCheckboxField('What brings you spiritual fulfillment?',
                                             choices=SPIRITUAL_FULFILLMENT,
                                             validators=[DataRequired()])

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

@app.before_first_request
def create_tables():
    db.create_all()

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
                love_activities=','.join(form.love_activities.data),
                love_topics=','.join(form.love_topics.data),
                skills_natural=','.join(form.skills_natural.data),
                skills_compliments=','.join(form.skills_compliments.data),
                world_problems=','.join(form.world_problems.data),
                world_impact=','.join(form.world_impact.data),
                spiritual_service=','.join(form.spiritual_service.data),
                spiritual_fulfillment=','.join(form.spiritual_fulfillment.data)
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
            keywords.extend(field.split(','))
    
    # Spiritual gifts mapping based on selected options
    spiritual_gifts_mapping = {
        'teaching': ['teaching', 'education', 'explaining', 'workshops'],
        'service': ['volunteering', 'community', 'giving'],
        'leadership': ['leadership', 'organizing', 'guidance'],
        'mercy': ['counseling', 'empathy', 'listening', 'patience'],
        'giving': ['giving', 'dedication', 'reliability'],
        'encouragement': ['motivation', 'positivity', 'growth'],
        'wisdom': ['wisdom', 'mindfulness', 'analytical'],
        'creativity': ['creativity', 'art', 'design', 'music'],
        'evangelism': ['faith', 'spiritual', 'pastoral'],
        'administration': ['organization', 'leadership', 'planning']
    }
    
    # Find matching spiritual gifts
    matched_gifts = []
    for gift, indicators in spiritual_gifts_mapping.items():
        if any(indicator in keywords for indicator in indicators):
            matched_gifts.append(gift)
    
    # Generate purpose statement
    purpose_statement = f"Based on your assessment, you have a calling towards {', '.join(matched_gifts)} roles. " \
                        f"Your unique combination of skills, passions, and values suggests you can make a significant " \
                        f"impact by focusing on areas that align with your spiritual gifts."
    
    return {
        'spiritual_gifts': matched_gifts,
        'purpose_statement': purpose_statement,
        'keywords': keywords
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
