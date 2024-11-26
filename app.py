from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired
from datetime import datetime
import os
import pdfkit
from flask_mail import Mail, Message
import tempfile
from functools import wraps
import re
import ssl
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_DEBUG'] = True  # Enable debug logging

# Add SSL context configuration
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Database Configuration
database_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///purpose_finder.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
mail = Mail(app)

# Custom validator for minimum selections
def at_least_one_required(form, field):
    if not field.data:
        raise ValidationError('Please select at least one option.')

# Custom widget for multiple select with checkboxes
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Assessment options
LOVE_ACTIVITIES = [
    ('creative_expression', 'Creative Expression'),
    ('physical_activity', 'Physical Activity'),
    ('learning_discovery', 'Learning & Discovery'),
    ('helping_others', 'Helping Others'),
    ('nature_outdoors', 'Nature & Outdoors'),
    ('tech_innovation', 'Technology & Innovation')
]

LOVE_TOPICS = [
    ('arts_culture', 'Arts & Culture'),
    ('social_connection', 'Social Connection'),
    ('problem_solving', 'Problem Solving'),
    ('music_sound', 'Music & Sound'),
    ('writing_communication', 'Writing & Communication'),
    ('personal_growth', 'Personal Growth')
]

SKILLS_NATURAL = [
    ('leadership', 'Leadership'),
    ('analysis', 'Analysis'),
    ('communication', 'Communication'),
    ('creativity', 'Creativity'),
    ('technical', 'Technical Skills'),
    ('organization', 'Organization')
]

SKILLS_COMPLIMENTS = [
    ('problem_solving', 'Problem Solving'),
    ('teaching', 'Teaching'),
    ('empathy', 'Empathy'),
    ('strategic_thinking', 'Strategic Thinking'),
    ('adaptability', 'Adaptability'),
    ('innovation', 'Innovation')
]

WORLD_PROBLEMS = [
    ('environmental', 'Environmental Protection'),
    ('education', 'Education Access'),
    ('healthcare', 'Healthcare Innovation'),
    ('social_justice', 'Social Justice'),
    ('mental_health', 'Mental Health Support'),
    ('tech_access', 'Technology Access')
]

WORLD_IMPACT = [
    ('food_security', 'Food Security'),
    ('economic_equality', 'Economic Equality'),
    ('clean_energy', 'Clean Energy'),
    ('community_building', 'Community Building'),
    ('digital_privacy', 'Digital Privacy'),
    ('sustainable_living', 'Sustainable Living')
]

NATURAL_ABILITIES = [
    ('tech_development', 'Technology Development'),
    ('healthcare_services', 'Healthcare Services'),
    ('education_training', 'Education & Training'),
    ('business_consulting', 'Business Consulting'),
    ('creative_services', 'Creative Services'),
    ('research_analysis', 'Research & Analysis')
]

INNATE_STRENGTHS = [
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
    love_activities = MultiCheckboxField('Activities that bring you joy',
        choices=LOVE_ACTIVITIES,
        validators=[at_least_one_required])
    
    love_topics = MultiCheckboxField('Topics that interest you',
        choices=LOVE_TOPICS,
        validators=[at_least_one_required])

    # What You're Good At
    skills_natural = MultiCheckboxField('Skills that come naturally',
        choices=SKILLS_NATURAL,
        validators=[at_least_one_required])
    
    skills_compliments = MultiCheckboxField('Skills others compliment you on',
        choices=SKILLS_COMPLIMENTS,
        validators=[at_least_one_required])

    # What the World Needs
    world_problems = MultiCheckboxField('Problems you want to solve',
        choices=WORLD_PROBLEMS,
        validators=[at_least_one_required])
    
    world_impact = MultiCheckboxField('Ways you want to make an impact',
        choices=WORLD_IMPACT,
        validators=[at_least_one_required])

    # Natural Talents
    natural_abilities = MultiCheckboxField('Your natural abilities',
        choices=NATURAL_ABILITIES,
        validators=[at_least_one_required])
    
    innate_strengths = MultiCheckboxField('Your innate strengths',
        choices=INNATE_STRENGTHS,
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
    form = AssessmentForm()
    return render_template('index.html', form=form)

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    form = AssessmentForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Get selected values
                love_activities = form.love_activities.data if form.love_activities.data else []
                love_topics = form.love_topics.data if form.love_topics.data else []
                skills_natural = form.skills_natural.data if form.skills_natural.data else []
                skills_compliments = form.skills_compliments.data if form.skills_compliments.data else []
                world_problems = form.world_problems.data if form.world_problems.data else []
                world_impact = form.world_impact.data if form.world_impact.data else []
                natural_abilities = form.natural_abilities.data if form.natural_abilities.data else []
                innate_strengths = form.innate_strengths.data if form.innate_strengths.data else []
                
                # Create new assessment
                assessment = Assessment(
                    love_activities=','.join(love_activities),
                    love_topics=','.join(love_topics),
                    skills_natural=','.join(skills_natural),
                    skills_compliments=','.join(skills_compliments),
                    world_problems=','.join(world_problems),
                    world_impact=','.join(world_impact),
                    natural_abilities=','.join(natural_abilities),
                    innate_strengths=','.join(innate_strengths)
                )
                
                # Save to database
                db.session.add(assessment)
                db.session.commit()
                
                # Get display values for results
                love_activities_display = [dict(LOVE_ACTIVITIES).get(x, '') for x in love_activities]
                love_topics_display = [dict(LOVE_TOPICS).get(x, '') for x in love_topics]
                skills_natural_display = [dict(SKILLS_NATURAL).get(x, '') for x in skills_natural]
                skills_compliments_display = [dict(SKILLS_COMPLIMENTS).get(x, '') for x in skills_compliments]
                world_problems_display = [dict(WORLD_PROBLEMS).get(x, '') for x in world_problems]
                world_impact_display = [dict(WORLD_IMPACT).get(x, '') for x in world_impact]
                natural_abilities_display = [dict(NATURAL_ABILITIES).get(x, '') for x in natural_abilities]
                innate_strengths_display = [dict(INNATE_STRENGTHS).get(x, '') for x in innate_strengths]
                
                # Process results
                results = {
                    'love_activities': love_activities_display,
                    'love_topics': love_topics_display,
                    'skills_natural': skills_natural_display,
                    'skills_compliments': skills_compliments_display,
                    'world_problems': world_problems_display,
                    'world_impact': world_impact_display,
                    'natural_abilities': natural_abilities_display,
                    'innate_strengths': innate_strengths_display,
                    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'passion_emotion': '',  
                    'mission_emotion': '',
                    'profession_emotion': '',
                    'vocation_emotion': ''
                }
                
                # Generate purpose statement
                results['purpose_statement'] = generate_purpose_statement(
                    love_activities_display,
                    love_topics_display,
                    skills_natural_display,
                    skills_compliments_display,
                    world_problems_display,
                    world_impact_display,
                    natural_abilities_display,
                    innate_strengths_display
                )
                
                session['assessment_results'] = results
                
                return render_template('results.html', results=results)
                
            except Exception as e:
                db.session.rollback()
                print(f'Error details: {str(e)}')  
                flash(f'Error saving assessment: {str(e)}', 'error')
                return render_template('assessment.html', form=form)
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'error')
            return render_template('assessment.html', form=form)
    
    # GET request - show empty form
    return render_template('assessment.html', form=form)

def generate_purpose_statement(
    love_activities,
    love_topics,
    skills_natural,
    skills_compliments,
    world_problems,
    world_impact,
    natural_abilities,
    innate_strengths
):
    """Generate a personalized purpose statement based on assessment choices."""
    
    # Ensure all inputs are lists and not None
    love_activities = love_activities if isinstance(love_activities, list) and love_activities else ['your interests']
    skills_natural = skills_natural if isinstance(skills_natural, list) and skills_natural else ['your abilities']
    world_problems = world_problems if isinstance(world_problems, list) and world_problems else ['global challenges']
    natural_abilities = natural_abilities if isinstance(natural_abilities, list) and natural_abilities else ['your work']
    
    # Create personalized statement components
    passion = f"Your passion lies in {' and '.join(love_activities[:2])}"
    mission = f"You have natural talents in {' and '.join(skills_natural[:2])}"
    vision = f"You're driven to address {' and '.join(world_problems[:2])}"
    profession = f"You can create value through {' and '.join(natural_abilities[:2])}"
    
    # Combine into final statement
    purpose_statement = f"""Your Ikigai reveals a unique and meaningful path: {passion}. 
    {mission}, while {vision.lower()}. 
    {profession}, bringing together your talents and the world's needs.
    
    This powerful combination suggests you could thrive in roles that combine your love for {love_activities[0].lower()} 
    with your natural {skills_natural[0].lower()}, 
    while addressing {world_problems[0].lower()} 
    through {natural_abilities[0].lower()}.
    
    Consider exploring career paths or projects that allow you to:
    1. Use your passion for {love_activities[0].lower()} to inspire and engage others
    2. Apply your {skills_natural[0].lower()} to solve real-world challenges
    3. Make a difference in {world_problems[0].lower()}
    4. Create value through {natural_abilities[0].lower()}"""
    
    return purpose_statement

def generate_pdf(results):
    """Generate a PDF file from the results."""
    # Ensure all values are converted to strings and have default values
    safe_results = {
        'love_activities': results.get('love_activities', []),
        'love_topics': results.get('love_topics', []),
        'skills_natural': results.get('skills_natural', []),
        'skills_compliments': results.get('skills_compliments', []),
        'world_problems': results.get('world_problems', []),
        'world_impact': results.get('world_impact', []),
        'natural_abilities': results.get('natural_abilities', []),
        'innate_strengths': results.get('innate_strengths', []),
        'purpose_statement': results.get('purpose_statement', 'No purpose statement generated.'),
        'passion_emotion': results.get('passion_emotion', 'Undefined'),
        'mission_emotion': results.get('mission_emotion', 'Undefined'),
        'profession_emotion': results.get('profession_emotion', 'Undefined'),
        'vocation_emotion': results.get('vocation_emotion', 'Undefined')
    }
    
    # Convert lists to comma-separated strings for better readability
    for key, value in safe_results.items():
        if isinstance(value, list):
            safe_results[key] = ', '.join(value) if value else 'None selected'
    
    # Create a temporary HTML file with the results
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        html_content = render_template('pdf_template.html', results=safe_results)
        f.write(html_content.encode('utf-8'))
        temp_html = f.name

    # Generate PDF from the HTML
    pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    pdfkit.from_file(temp_html, pdf_file.name)
    
    # Clean up the temporary HTML file
    os.unlink(temp_html)
    
    return pdf_file.name

def send_results_email(email, results):
    """Send results to the specified email address."""
    try:
        # Ensure all values are converted to strings and have default values
        safe_results = {
            'love_activities': results.get('love_activities', []),
            'love_topics': results.get('love_topics', []),
            'skills_natural': results.get('skills_natural', []),
            'skills_compliments': results.get('skills_compliments', []),
            'world_problems': results.get('world_problems', []),
            'world_impact': results.get('world_impact', []),
            'natural_abilities': results.get('natural_abilities', []),
            'innate_strengths': results.get('innate_strengths', []),
            'purpose_statement': results.get('purpose_statement', 'No purpose statement generated.'),
            'passion_emotion': results.get('passion_emotion', 'Undefined'),
            'mission_emotion': results.get('mission_emotion', 'Undefined'),
            'profession_emotion': results.get('profession_emotion', 'Undefined'),
            'vocation_emotion': results.get('vocation_emotion', 'Undefined')
        }
        
        # Convert lists to comma-separated strings for better readability
        for key, value in safe_results.items():
            if isinstance(value, list):
                safe_results[key] = ', '.join(value) if value else 'None selected'
        
        # Create message
        msg = Message(
            'Your Ikigai Purpose Discovery Results',
            recipients=[email],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg.body = f"""
        Thank you for completing the Ikigai Purpose Discovery assessment!
        
        Purpose Statement:
        {safe_results['purpose_statement']}
        
        Key Insights:
        - Love Activities: {safe_results['love_activities']}
        - Love Topics: {safe_results['love_topics']}
        - Natural Skills: {safe_results['skills_natural']}
        - Complimented Skills: {safe_results['skills_compliments']}
        - World Problems: {safe_results['world_problems']}
        - Impact Areas: {safe_results['world_impact']}
        - Natural Abilities: {safe_results['natural_abilities']}
        - Innate Strengths: {safe_results['innate_strengths']}
        
        Emotional Dimensions:
        - Passion Emotion: {safe_results['passion_emotion']}
        - Mission Emotion: {safe_results['mission_emotion']}
        - Profession Emotion: {safe_results['profession_emotion']}
        - Vocation Emotion: {safe_results['vocation_emotion']}
        
        Please find your personalized results attached to this email.
        
        Best regards,
        The Ikigai Purpose Discovery Team
        """
        
        # Generate PDF
        pdf_path = generate_pdf(safe_results)
        
        # Attach PDF
        with open(pdf_path, 'rb') as f:
            msg.attach(
                filename='ikigai_results.pdf', 
                content_type='application/pdf', 
                data=f.read()
            )
        
        # Send email with enhanced error handling
        try:
            mail.send(msg)
            print(f"Email sent successfully to {email}")
            
            # Clean up PDF file
            os.unlink(pdf_path)
            
            return True
        except Exception as send_error:
            print(f"Detailed email sending error: {send_error}")
            # Log the full error traceback
            import traceback
            traceback.print_exc()
            return False
    
    except Exception as e:
        print(f"Error preparing email: {e}")
        # Log the full error traceback
        import traceback
        traceback.print_exc()
        return False

@app.route('/download_pdf')
def download_pdf():
    """Generate and download PDF of results."""
    try:
        # Retrieve results from the session
        results = session.get('assessment_results', {})
        
        # Ensure all values are converted to strings and have default values
        safe_results = {
            'love_activities': results.get('love_activities', []),
            'love_topics': results.get('love_topics', []),
            'skills_natural': results.get('skills_natural', []),
            'skills_compliments': results.get('skills_compliments', []),
            'world_problems': results.get('world_problems', []),
            'world_impact': results.get('world_impact', []),
            'natural_abilities': results.get('natural_abilities', []),
            'innate_strengths': results.get('innate_strengths', []),
            'purpose_statement': results.get('purpose_statement', 'No purpose statement generated.'),
            'passion_emotion': results.get('passion_emotion', 'Undefined'),
            'mission_emotion': results.get('mission_emotion', 'Undefined'),
            'profession_emotion': results.get('profession_emotion', 'Undefined'),
            'vocation_emotion': results.get('vocation_emotion', 'Undefined')
        }
        
        # Convert lists to comma-separated strings for better readability
        for key, value in safe_results.items():
            if isinstance(value, list):
                safe_results[key] = ', '.join(value) if value else 'None selected'
        
        # Generate PDF
        pdf_path = generate_pdf(safe_results)
        
        # Send the PDF file
        return send_file(
            pdf_path, 
            mimetype='application/pdf', 
            as_attachment=True, 
            download_name='ikigai_results.pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash('Error generating PDF. Please try again.', 'error')
        return redirect(url_for('results'))

@app.route('/email_results', methods=['POST'])
def email_results():
    """Email results to the specified address."""
    try:
        # Retrieve results from the session
        results = session.get('assessment_results', {})
        
        # Get email from form
        email = request.form.get('email')
        
        # Validate email
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address', 'error')
            return redirect(url_for('results'))
        
        # Ensure all values are converted to strings and have default values
        safe_results = {
            'love_activities': results.get('love_activities', []),
            'love_topics': results.get('love_topics', []),
            'skills_natural': results.get('skills_natural', []),
            'skills_compliments': results.get('skills_compliments', []),
            'world_problems': results.get('world_problems', []),
            'world_impact': results.get('world_impact', []),
            'natural_abilities': results.get('natural_abilities', []),
            'innate_strengths': results.get('innate_strengths', []),
            'purpose_statement': results.get('purpose_statement', 'No purpose statement generated.'),
            'passion_emotion': results.get('passion_emotion', 'Undefined'),
            'mission_emotion': results.get('mission_emotion', 'Undefined'),
            'profession_emotion': results.get('profession_emotion', 'Undefined'),
            'vocation_emotion': results.get('vocation_emotion', 'Undefined')
        }
        
        # Convert lists to comma-separated strings for better readability
        for key, value in safe_results.items():
            if isinstance(value, list):
                safe_results[key] = ', '.join(value) if value else 'None selected'
        
        # Send email
        if send_results_email(email, safe_results):
            flash('Results sent to your email successfully!', 'success')
        else:
            flash('Failed to send email. Please try again.', 'error')
        
        return redirect(url_for('results'))
    
    except Exception as e:
        print(f"Error emailing results: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('results'))

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging to file
    log_file = os.path.join(log_dir, 'ikigai_app.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024 * 1024 * 10,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Get the root logger and add handlers
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Call logging setup before running the app
setup_logging()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084)
