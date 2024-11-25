from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
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

# Custom widget for multiple select with checkboxes
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Assessment options
WORLD_PROBLEMS = [
    ('education', 'Access to quality education for all'),
    ('climate', 'Climate change and environmental protection'),
    ('inequality', 'Inequality and poverty reduction'),
    ('mental_health', 'Mental health awareness and support'),
    ('energy', 'Promoting sustainable energy solutions'),
    ('healthcare', 'Better healthcare accessibility'),
    ('cultural', 'Cultural understanding and harmony'),
    ('water', 'Access to clean water and sanitation'),
    ('youth', 'Youth empowerment and mentorship'),
    ('community', 'Community-building and social justice')
]

WORLD_IMPACT = [
    ('innovation', 'Developing innovative solutions for global challenges'),
    ('art', 'Inspiring others through art or storytelling'),
    ('education', 'Providing education and training for underserved populations'),
    ('sustainability', 'Building sustainable communities'),
    ('advocacy', 'Advocating for equal rights and opportunities'),
    ('spiritual', 'Empowering people through spiritual guidance'),
    ('growth', 'Offering tools for personal and professional growth'),
    ('science', 'Contributing to scientific discoveries or advancements'),
    ('awareness', 'Raising awareness of important global issues'),
    ('wellbeing', 'Supporting mental and emotional well-being')
]

SPIRITUAL_SERVICE = [
    ('teaching', 'Teaching and mentoring individuals'),
    ('volunteering', 'Volunteering for community services'),
    ('motivation', 'Sharing motivational messages or advice'),
    ('leadership', 'Leading by example in professional or personal settings'),
    ('counseling', 'Counseling or providing emotional support'),
    ('giving', 'Offering financial or material help to those in need'),
    ('organizing', 'Organizing charitable or fundraising events'),
    ('workshops', 'Hosting workshops or training sessions'),
    ('pastoral', 'Providing spiritual direction or pastoral care'),
    ('advocacy', 'Advocating for social causes')
]

SPIRITUAL_FULFILLMENT = [
    ('growth', 'Helping others grow and reach their potential'),
    ('impact', 'Witnessing positive changes in the lives of others'),
    ('mindfulness', 'Practicing gratitude and mindfulness'),
    ('wisdom', 'Sharing knowledge and wisdom'),
    ('causes', 'Contributing to meaningful and impactful causes'),
    ('community', 'Building strong relationships and communities'),
    ('faith', 'Inspiring others through faith or spirituality'),
    ('nature', 'Connecting with nature and the environment'),
    ('creativity', 'Creating art or music that touches lives'),
    ('mission', 'Being part of a larger mission or vision')
]

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
    
    # Career suggestions based on keywords
    career_mapping = {
        'Teacher/Educator': ['teaching', 'education', 'explaining'],
        'Counselor/Therapist': ['counseling', 'empathy', 'listening'],
        'Ministry Leader': ['leadership', 'spiritual', 'pastoral'],
        'Creative Professional': ['creativity', 'art', 'design'],
        'Community Organizer': ['community', 'organizing', 'advocacy'],
        'Environmental Advocate': ['environment', 'nature', 'sustainability'],
        'Healthcare Professional': ['healthcare', 'wellbeing', 'mental_health'],
        'Social Worker': ['service', 'counseling', 'community'],
        'Nonprofit Leader': ['leadership', 'advocacy', 'community'],
        'Technology Innovator': ['tech', 'innovation', 'problem_solving']
    }
    
    careers = []
    for career, indicators in career_mapping.items():
        if any(indicator in keywords for indicator in indicators):
            careers.append(career)
    
    # Generate personalized recommendations
    recommendations = []
    if matched_gifts:
        recommendations.append(f"Your spiritual gifts of {', '.join(matched_gifts)} align well with careers in {', '.join(careers)}.")
    
    # Add specific recommendations based on selected options
    if 'teaching' in keywords:
        recommendations.append("Your passion for teaching and explaining suggests you would excel in educational or mentoring roles.")
    if 'community' in keywords:
        recommendations.append("Your heart for community indicates you could make a significant impact through local outreach or nonprofit work.")
    if 'leadership' in keywords:
        recommendations.append("Your leadership abilities could be well-utilized in organizational or ministry leadership positions.")
    if 'creativity' in keywords:
        recommendations.append("Your creative gifts could be channeled into worship arts, media ministry, or creative education.")
    
    return {
        'spiritual_gifts': matched_gifts,
        'careers': careers,
        'recommendations': recommendations
    }

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create tables with new schema
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
