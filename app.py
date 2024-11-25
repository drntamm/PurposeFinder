from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets
from wtforms.validators import ValidationError
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

# Custom validator for minimum selections
def at_least_one_required(form, field):
    if not field.data:
        raise ValidationError('Please select at least one option.')

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
                                       validators=[at_least_one_required])
    love_topics = MultiCheckboxField('What topics interest you the most?',
                                    choices=LOVE_TOPICS,
                                    validators=[at_least_one_required])
    skills_natural = MultiCheckboxField('What are your natural skills?',
                                      choices=NATURAL_SKILLS,
                                      validators=[at_least_one_required])
    skills_compliments = MultiCheckboxField('What do people compliment you on?',
                                          choices=COMPLIMENTS,
                                          validators=[at_least_one_required])
    world_problems = MultiCheckboxField('What problems do you want to solve?',
                                      choices=WORLD_PROBLEMS,
                                      validators=[at_least_one_required])
    world_impact = MultiCheckboxField('How do you want to impact the world?',
                                    choices=WORLD_IMPACT,
                                    validators=[at_least_one_required])
    spiritual_service = MultiCheckboxField('How do you like to serve others?',
                                         choices=SPIRITUAL_SERVICE,
                                         validators=[at_least_one_required])
    spiritual_fulfillment = MultiCheckboxField('What brings you spiritual fulfillment?',
                                             choices=SPIRITUAL_FULFILLMENT,
                                             validators=[at_least_one_required])

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

# Initialize database before first request
@app.before_first_request
def init_db():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    form = AssessmentForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
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
                flash(f'Error saving assessment: {str(e)}', 'error')
                return render_template('assessment.html', form=form)
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'error')
    
    return render_template('assessment.html', form=form)

def analyze_assessment(assessment):
    # Extract individual responses
    love_activities = assessment.love_activities.split(',')
    love_topics = assessment.love_topics.split(',')
    skills_natural = assessment.skills_natural.split(',')
    skills_compliments = assessment.skills_compliments.split(',')
    world_problems = assessment.world_problems.split(',')
    world_impact = assessment.world_impact.split(',')
    spiritual_service = assessment.spiritual_service.split(',')
    spiritual_fulfillment = assessment.spiritual_fulfillment.split(',')

    # Prepare Venn diagram data
    love_items = [item.replace('_', ' ').title() for item in (love_activities[:2] + love_topics[:2])]
    good_at_items = [item.replace('_', ' ').title() for item in (skills_natural[:2] + skills_compliments[:2])]
    world_needs_items = [item.replace('_', ' ').title() for item in (world_problems[:2] + world_impact[:2])]
    natural_talents_items = [item.replace('_', ' ').title() for item in (spiritual_service[:2] + spiritual_fulfillment[:2])]

    # Generate career suggestions
    careers = [
        "Career Coach",
        "Non-profit Leader",
        "Community Organizer",
        "Educational Consultant",
        "Social Entrepreneur"
    ]

    # Generate recommendations
    recommendations = [
        f"Focus on combining your love of {love_items[0].lower()} with your talent for {good_at_items[0].lower()}",
        f"Consider how you can address {world_needs_items[0].lower()} using your {natural_talents_items[0].lower()} abilities",
        f"Develop your skills in {good_at_items[1].lower()} to make a bigger impact in {world_needs_items[1].lower()}",
        "Network with professionals in your areas of interest",
        "Seek mentorship opportunities in your chosen field"
    ]

    return {
        'love_items': love_items,
        'good_at_items': good_at_items,
        'world_needs_items': world_needs_items,
        'natural_talents_items': natural_talents_items,
        'natural_talents': [item.replace('_', ' ').title() for item in (spiritual_service + spiritual_fulfillment)],
        'careers': careers,
        'recommendations': recommendations
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
