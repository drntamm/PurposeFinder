from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired
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
LOVE_OPTIONS = [
    ('creative_expression', 'Creative Expression'),
    ('learning_discovery', 'Learning & Discovery'),
    ('helping_others', 'Helping Others'),
    ('nature_outdoors', 'Nature & Outdoors'),
    ('tech_innovation', 'Technology & Innovation'),
    ('physical_activity', 'Physical Activity'),
    ('arts_culture', 'Arts & Culture'),
    ('social_connection', 'Social Connection'),
    ('problem_solving', 'Problem Solving'),
    ('music_sound', 'Music & Sound'),
    ('writing_communication', 'Writing & Communication'),
    ('personal_growth', 'Personal Growth')
]

SKILLS_OPTIONS = [
    ('leadership', 'Leadership'),
    ('analysis', 'Analysis'),
    ('communication', 'Communication'),
    ('creativity', 'Creativity'),
    ('technical_expertise', 'Technical Expertise'),
    ('organization', 'Organization'),
    ('problem_solving', 'Problem Solving'),
    ('teaching', 'Teaching'),
    ('empathy', 'Empathy'),
    ('strategic_thinking', 'Strategic Thinking'),
    ('adaptability', 'Adaptability'),
    ('innovation', 'Innovation')
]

WORLD_NEEDS_OPTIONS = [
    ('environmental_protection', 'Environmental Protection'),
    ('education_access', 'Education Access'),
    ('healthcare_innovation', 'Healthcare Innovation'),
    ('social_justice', 'Social Justice'),
    ('mental_health', 'Mental Health Support'),
    ('tech_access', 'Technology Access'),
    ('food_security', 'Food Security'),
    ('economic_equality', 'Economic Equality'),
    ('clean_energy', 'Clean Energy'),
    ('community_building', 'Community Building'),
    ('digital_privacy', 'Digital Privacy'),
    ('sustainable_living', 'Sustainable Living')
]

PROFESSION_OPTIONS = [
    ('tech_development', 'Technology Development'),
    ('healthcare_services', 'Healthcare Services'),
    ('education_training', 'Education & Training'),
    ('business_consulting', 'Business Consulting'),
    ('creative_services', 'Creative Services'),
    ('research_analysis', 'Research & Analysis'),
    ('project_management', 'Project Management'),
    ('social_services', 'Social Services'),
    ('environmental_work', 'Environmental Work'),
    ('content_creation', 'Content Creation'),
    ('financial_services', 'Financial Services'),
    ('entrepreneurship', 'Entrepreneurship')
]

# Form Class
class AssessmentForm(FlaskForm):
    # What You Love
    love_options = SelectMultipleField('What activities bring you joy?',
        choices=LOVE_OPTIONS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    # What You're Good At
    skills_options = SelectMultipleField('What skills come naturally to you?',
        choices=SKILLS_OPTIONS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

    # What the World Needs
    world_needs_options = SelectMultipleField('What problems in the world concern you most?',
        choices=WORLD_NEEDS_OPTIONS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    profession_options = SelectMultipleField('How would you like to make a difference?',
        choices=PROFESSION_OPTIONS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

# Database Models
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    love_options = db.Column(db.Text)
    skills_options = db.Column(db.Text)
    world_needs_options = db.Column(db.Text)
    profession_options = db.Column(db.Text)

# Initialize database before first request
@app.before_first_request
def init_db():
    with app.app_context():
        # Drop all tables to handle renamed columns
        db.drop_all()
        # Create all tables with new schema
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
                    love_options=','.join(form.love_options.data),
                    skills_options=','.join(form.skills_options.data),
                    world_needs_options=','.join(form.world_needs_options.data),
                    profession_options=','.join(form.profession_options.data)
                )
                
                # Save to database
                db.session.add(assessment)
                db.session.commit()
                
                # Process results
                results = {
                    'love_options': form.love_options.data,
                    'skills_options': form.skills_options.data,
                    'world_needs_options': form.world_needs_options.data,
                    'profession_options': form.profession_options.data,
                    'purpose_statement': generate_purpose_statement(form)
                }
                
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

def generate_purpose_statement(form_data):
    """Generate a personalized purpose statement based on assessment choices."""
    
    # Get the text values (not codes) from the selected options
    love_choices = [dict(LOVE_OPTIONS).get(choice) for choice in form_data.love_options.data]
    skills_choices = [dict(SKILLS_OPTIONS).get(choice) for choice in form_data.skills_options.data]
    world_choices = [dict(WORLD_NEEDS_OPTIONS).get(choice) for choice in form_data.world_needs_options.data]
    profession_choices = [dict(PROFESSION_OPTIONS).get(choice) for choice in form_data.profession_options.data]
    
    # Create personalized statement components
    passion = f"Your passion lies in {' and '.join(love_choices[:2])}"
    mission = f"You have natural talents in {' and '.join(skills_choices[:2])}"
    vision = f"You're driven to address {' and '.join(world_choices[:2])}"
    profession = f"You can create value through {' and '.join(profession_choices[:2])}"
    
    # Combine into final statement
    purpose_statement = f"""Your Ikigai reveals a unique and meaningful path: {passion}. 
    {mission}, while {vision.lower()}. 
    {profession}, bringing together your talents and the world's needs.
    
    This powerful combination suggests you could thrive in roles that combine your love for {love_choices[0].lower()} 
    with your natural {skills_choices[0].lower()} abilities, 
    while addressing {world_choices[0].lower()} through {profession_choices[0].lower()}.
    
    Consider exploring career paths or projects that allow you to:
    1. Use your passion for {love_choices[0].lower()} to inspire and engage others
    2. Apply your {skills_choices[0].lower()} skills to solve real-world challenges
    3. Make a difference in {world_choices[0].lower()}
    4. Create value through {profession_choices[0].lower()}
    
    Remember that your Ikigai is not just about finding a job - it's about discovering where your gifts intersect 
    with the world's needs in a way that brings you joy and sustains you."""
    
    return purpose_statement

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8081)))
