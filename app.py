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

NATURAL_ABILITIES = [
    ('analytical', 'Strong analytical and problem-solving abilities'),
    ('interpersonal', 'Natural interpersonal and relationship-building skills'),
    ('creative', 'Creative thinking and innovative ideation'),
    ('strategic', 'Strategic planning and vision development'),
    ('empathetic', 'Deep empathy and emotional intelligence'),
    ('technical', 'Technical aptitude and quick learning'),
    ('communication', 'Clear and effective communication'),
    ('leadership', 'Natural leadership and team motivation'),
    ('adaptability', 'Adaptability and resilience'),
    ('organization', 'Exceptional organizational abilities')
]

INNATE_STRENGTHS = [
    ('intuition', 'Strong intuition and insight'),
    ('persistence', 'Natural persistence and determination'),
    ('synthesis', 'Ability to synthesize complex information'),
    ('inspiration', 'Talent for inspiring and motivating others'),
    ('perception', 'Keen perception and observation skills'),
    ('diplomacy', 'Natural diplomacy and conflict resolution'),
    ('innovation', 'Innovative thinking and problem-solving'),
    ('mentoring', 'Natural mentoring and teaching abilities'),
    ('coordination', 'Excellent project coordination skills'),
    ('vision', 'Visionary thinking and future planning')
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
    # What You Love
    love_activities = SelectMultipleField('What activities bring you joy?',
        choices=LOVE_ACTIVITIES,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    love_topics = SelectMultipleField('What topics fascinate you?',
        choices=LOVE_TOPICS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

    # What You're Good At
    skills_natural = SelectMultipleField('What skills come naturally to you?',
        choices=NATURAL_SKILLS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    skills_compliments = SelectMultipleField('What do people often compliment you on?',
        choices=COMPLIMENTS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

    # What the World Needs
    world_problems = SelectMultipleField('What problems in the world concern you most?',
        choices=WORLD_PROBLEMS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    world_impact = SelectMultipleField('How would you like to make a difference?',
        choices=WORLD_IMPACT,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

    # Natural Talents
    natural_abilities = SelectMultipleField('What are your core natural abilities?',
        choices=NATURAL_ABILITIES,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    
    innate_strengths = SelectMultipleField('What are your innate personal strengths?',
        choices=INNATE_STRENGTHS,
        validators=[DataRequired()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

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
    natural_abilities = db.Column(db.Text)
    innate_strengths = db.Column(db.Text)

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
                    love_activities=','.join(form.love_activities.data),
                    love_topics=','.join(form.love_topics.data),
                    skills_natural=','.join(form.skills_natural.data),
                    skills_compliments=','.join(form.skills_compliments.data),
                    world_problems=','.join(form.world_problems.data),
                    world_impact=','.join(form.world_impact.data),
                    natural_abilities=','.join(form.natural_abilities.data),
                    innate_strengths=','.join(form.innate_strengths.data)
                )
                
                # Save to database
                db.session.add(assessment)
                db.session.commit()
                
                # Process results
                results = {
                    'love_activities': form.love_activities.data,
                    'love_topics': form.love_topics.data,
                    'skills_natural': form.skills_natural.data,
                    'skills_compliments': form.skills_compliments.data,
                    'world_problems': form.world_problems.data,
                    'world_impact': form.world_impact.data,
                    'natural_abilities': form.natural_abilities.data,
                    'innate_strengths': form.innate_strengths.data,
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

def generate_purpose_statement(form):
    """Generate a personalized purpose statement based on form responses."""
    loves = form.love_activities.data + form.love_topics.data
    skills = form.skills_natural.data + form.skills_compliments.data
    impact = form.world_problems.data + form.world_impact.data
    talents = form.natural_abilities.data + form.innate_strengths.data
    
    # Select key elements for the purpose statement
    primary_love = loves[0] if loves else ""
    primary_skill = skills[0] if skills else ""
    primary_impact = impact[0] if impact else ""
    primary_talent = talents[0] if talents else ""
    
    statement = f"Your purpose may be to use your natural talent for {primary_talent} "
    statement += f"and your skill in {primary_skill} "
    statement += f"to {primary_impact}, "
    statement += f"while pursuing your passion for {primary_love}."
    
    return statement

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8081)))
