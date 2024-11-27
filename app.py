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
LOVE_ACTIVITIES = [
    ('creative_expression', 'Creating Art and Written Content'),
    ('problem_solving', 'Finding Solutions to Complex Challenges'),
    ('helping_others', 'Guiding and Supporting People'),
    ('learning_growth', 'Pursuing Knowledge and Growth'),
    ('physical_activity', 'Engaging in Active Movement'),
    ('building_things', 'Crafting and Building Projects'),
    ('organizing', 'Structuring and Planning Activities'),
    ('communicating', 'Fostering Meaningful Connections'),
    ('exploring', 'Discovering New Possibilities'),
    ('leading_others', 'Guiding and Motivating Teams'),
    ('analyzing_data', 'Understanding Patterns in Information'),
    ('performing', 'Sharing Through Performance')
]

LOVE_TOPICS = [
    ('technology', 'Digital Innovation and Advancement'),
    ('arts_culture', 'Cultural Expression and Heritage'),
    ('science_discovery', 'Scientific Research and Discovery'),
    ('social_impact', 'Creating Positive Social Change'),
    ('health_wellness', 'Personal Health and Wellbeing'),
    ('education_learning', 'Teaching and Knowledge Sharing'),
    ('nature_environment', 'Environmental Studies and Conservation'),
    ('business_entrepreneurship', 'Business Creation and Growth'),
    ('spirituality_philosophy', 'Spiritual and Philosophical Inquiry'),
    ('sports_recreation', 'Sports and Active Living'),
    ('media_entertainment', 'Media Production and Content'),
    ('design_aesthetics', 'Visual Design and Aesthetics')
]

NATURAL_SKILLS = [
    ('critical_thinking', 'Analyzing Complex Situations'),
    ('creativity', 'Generating Innovative Ideas'),
    ('communication', 'Expressing Ideas Clearly'),
    ('leadership', 'Inspiring and Guiding Others'),
    ('technical_skills', 'Mastering Digital Tools'),
    ('empathy', 'Understanding Others Deeply'),
    ('organization', 'Creating Effective Systems'),
    ('problem_solving', 'Developing Strategic Solutions'),
    ('adaptability', 'Thriving in Change'),
    ('research', 'Investigating and Discovering'),
    ('teamwork', 'Building Strong Partnerships'),
    ('decision_making', 'Making Thoughtful Choices')
]

COMPLIMENTS = [
    ('reliability', 'Being Consistently Dependable'),
    ('innovation', 'Creating Novel Solutions'),
    ('leadership_ability', 'Inspiring Others Naturally'),
    ('communication_style', 'Connecting Effectively'),
    ('problem_solving_approach', 'Resolving Challenges Skillfully'),
    ('emotional_support', 'Offering Genuine Support'),
    ('technical_expertise', 'Understanding Complex Systems'),
    ('organization_skills', 'Managing Resources Effectively'),
    ('teaching_ability', 'Sharing Knowledge Clearly'),
    ('artistic_talent', 'Creating Beautiful Work'),
    ('analytical_thinking', 'Processing Information Logically'),
    ('team_collaboration', 'Working Together Harmoniously')
]

WORLD_PROBLEMS = [
    ('education access', 'Making Education Available to All'),
    ('environmental care', 'Protecting Our Environment'),
    ('healthcare access', 'Improving Healthcare Access'),
    ('social equality', 'Building a Fair Society'),
    ('mental wellness', 'Supporting Emotional Wellbeing'),
    ('technology ethics', 'Ensuring Responsible Innovation'),
    ('community growth', 'Strengthening Local Communities'),
    ('economic growth', 'Creating Economic Growth'),
    ('cultural heritage', 'Preserving Cultural Heritage'),
    ('human progress', 'Advancing Human Progress'),
    ('peace building', 'Fostering Peace and Understanding'),
    ('future sustainability', 'Creating a Sustainable Future')
]

WORLD_IMPACT = [
    ('teach and inspire', 'Teaching and Inspiring Growth'),
    ('solve challenges', 'Creating Lasting Solutions'),
    ('spark innovation', 'Developing New Possibilities'),
    ('support growth', 'Supporting Personal Growth'),
    ('unite communities', 'Uniting People and Places'),
    ('advance progress', 'Moving Technology Forward'),
    ('protect earth', 'Protecting Our Planet'),
    ('promote justice', 'Standing for Fairness'),
    ('nurture wellness', 'Nurturing Health and Happiness'),
    ('preserve culture', 'Celebrating Cultural Heritage'),
    ('encourage ideas', 'Encouraging New Ideas'),
    ('enable success', 'Enabling Personal Success')
]

NATURAL_ABILITIES = [
    ('rapid learning', 'Grasping New Concepts Quickly'),
    ('idea generation', 'Imagining New Possibilities'),
    ('systems thinking', 'Understanding Complex Systems'),
    ('people insight', 'Reading People and Situations'),
    ('physical grace', 'Moving with Natural Grace'),
    ('clear speaking', 'Speaking with Impact'),
    ('pattern recognition', 'Seeing Patterns and Connections'),
    ('musical sense', 'Understanding Sound and Rhythm'),
    ('social connection', 'Connecting with Others Naturally'),
    ('future planning', 'Planning for Success'),
    ('tech intuition', 'Understanding Technology Naturally'),
    ('people guidance', 'Guiding Others Effectively')
]

INNATE_STRENGTHS = [
    ('bounce back', 'Bouncing Back from Challenges'),
    ('natural curiosity', 'Exploring with Wonder'),
    ('deep empathy', 'Understanding Others Hearts'),
    ('quick adapting', 'Embracing Change Readily'),
    ('goal pursuit', 'Pursuing Goals Relentlessly'),
    ('creative vision', 'Seeing New Possibilities'),
    ('logical analysis', 'Breaking Down Complex Ideas'),
    ('inner wisdom', 'Following Inner Wisdom'),
    ('natural order', 'Creating Order Naturally'),
    ('natural leading', 'Taking Initiative Naturally'),
    ('clear expression', 'Sharing Ideas Effectively'),
    ('solution finding', 'Finding Creative Solutions')
]

# Form Class
class AssessmentForm(FlaskForm):
    # What You Love
    love_activities = SelectMultipleField(
        'Activities You Love (Select all that apply to you)',
        choices=LOVE_ACTIVITIES,
        validators=[DataRequired('Please select at least one activity you love')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    
    love_topics = SelectMultipleField(
        'Topics You Love (Select all that apply to you)',
        choices=LOVE_TOPICS,
        validators=[DataRequired('Please select at least one topic you love')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    # What You're Good At
    skills_natural = SelectMultipleField(
        'Natural Skills (Select all that apply to you)',
        choices=NATURAL_SKILLS,
        validators=[DataRequired('Please select at least one natural skill')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    
    skills_compliments = SelectMultipleField(
        'Skills Others Compliment (Select all that apply to you)',
        choices=COMPLIMENTS,
        validators=[DataRequired('Please select at least one skill others compliment')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    # What the World Needs
    world_problems = SelectMultipleField(
        'World Problems You Want to Solve (Select all that apply to you)',
        choices=WORLD_PROBLEMS,
        validators=[DataRequired('Please select at least one world problem')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    
    world_impact = SelectMultipleField(
        'Ways You Want to Impact the World (Select all that apply to you)',
        choices=WORLD_IMPACT,
        validators=[DataRequired('Please select at least one way to impact')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    # Natural Talents
    natural_abilities = SelectMultipleField(
        'Your Natural Abilities (Select all that apply to you)',
        choices=NATURAL_ABILITIES,
        validators=[DataRequired('Please select at least one natural ability')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    
    innate_strengths = SelectMultipleField(
        'Your Innate Strengths (Select all that apply to you)',
        choices=INNATE_STRENGTHS,
        validators=[DataRequired('Please select at least one innate strength')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

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
                    'purpose_statement': generate_purpose_statement(form),
                    'career_recommendations': generate_career_recommendations(form.love_activities.data + form.love_topics.data),
                    'activity_descriptions': get_activity_descriptions(form.love_activities.data + form.love_topics.data, 'passion'),
                    'talent_descriptions': get_talent_descriptions(form.natural_abilities.data + form.innate_strengths.data),
                    'learning_resources': get_learning_resources(form.love_activities.data + form.love_topics.data + form.skills_natural.data + form.skills_compliments.data)
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
    """Generate an articulate purpose statement using NLP patterns and selected responses."""
    
    # Extract selections from each category
    passions = list(form.love_activities.data) + list(form.love_topics.data)
    talents = list(form.natural_abilities.data) + list(form.innate_strengths.data)
    skills = list(form.skills_natural.data) + list(form.skills_compliments.data)
    impact_areas = list(form.world_problems.data) + list(form.world_impact.data)
    
    # Define statement templates with varying structures
    templates = [
        "Drawing from your {talents_skills}, you are uniquely positioned to contribute to {impact}. Your {passions_primary}, combined with {passions_secondary}, enhances your potential to make a meaningful impact. Additionally, your interest in {passions_additional} aligns with efforts to {impact_additional}.",
        "Your combination of {talents_skills} uniquely equips you to address {impact}. Through your dedication to {passions_primary} and {passions_secondary}, you can create lasting positive change. Moreover, your passion for {passions_additional} strengthens your ability to {impact_additional}.",
        "With your foundation in {talents_skills}, you have the potential to make significant contributions to {impact}. Your commitment to {passions_primary}, alongside {passions_secondary}, positions you to create meaningful change. Furthermore, your engagement with {passions_additional} enhances your capacity to {impact_additional}."
    ]
    
    def format_list_naturally(items):
        """Format a list of items into a natural phrase."""
        if not items:
            return ""
        
        # Remove empty strings
        items = [item.strip() for item in items if item.strip()]
        
        if len(items) == 0:
            return ""
        elif len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return f"{', '.join(items[:-1])}, and {items[-1]}"
    
    # Comprehensive mapping of raw values to natural phrases
    context_phrases = {
        'passion': {
            'creative_expression': 'creative expression and artistic innovation',
            'problem_solving': 'solving complex challenges',
            'helping_others': 'supporting and empowering others',
            'learning_growth': 'continuous learning and personal growth',
            'physical_activity': 'physical movement and active engagement',
            'building_things': 'creating and building meaningful projects',
            'organizing': 'bringing structure and order to systems',
            'communicating': 'fostering meaningful connections',
            'exploring': 'exploring new possibilities',
            'leading_others': 'guiding and inspiring teams',
            'analyzing_data': 'uncovering insights from information',
            'performing': 'sharing through performance and presentation',
            'technology': 'advancing digital innovation',
            'arts_culture': 'preserving and promoting cultural expression',
            'science_discovery': 'scientific exploration and discovery',
            'social_impact': 'creating positive social change',
            'health_wellness': 'promoting health and wellness',
            'education_learning': 'sharing knowledge and fostering lifelong learning',
            'nature_environment': 'environmental stewardship and conservation',
            'business_entrepreneurship': 'building and growing impactful ventures',
            'spirituality_philosophy': 'exploring spiritual and philosophical depths',
            'sports_recreation': 'promoting active and healthy living',
            'media_entertainment': 'creating engaging and meaningful content',
            'design_aesthetics': 'crafting beautiful and purposeful experiences'
        },
        'talent': {
            'rapid_learning': 'rapid learning abilities',
            'idea_generation': 'innovative thinking capabilities',
            'systems_thinking': 'systems thinking approach',
            'people_insight': 'deep understanding of human dynamics',
            'clear_speaking': 'articulate communication skills',
            'adaptability': 'adaptability in changing environments',
            'creativity': 'creative problem-solving abilities',
            'empathy': 'strong emotional intelligence',
            'leadership': 'natural leadership qualities',
            'analysis': 'sharp analytical mindset',
            'teaching': 'gift for explaining complex concepts',
            'innovation': 'breakthrough thinking capabilities'
        },
        'skill': {
            'critical_thinking': 'critical analysis',
            'creativity': 'creative innovation',
            'communication': 'effective communication',
            'leadership': 'team leadership',
            'technical_skills': 'technical expertise',
            'empathy': 'emotional understanding',
            'organization': 'organizational excellence',
            'problem_solving': 'strategic problem-solving',
            'adaptability': 'adaptive thinking',
            'research': 'thorough research capabilities',
            'teamwork': 'collaborative excellence',
            'decision_making': 'sound decision-making'
        },
        'impact': {
            'education_access': 'educational accessibility and equity',
            'environmental_care': 'environmental sustainability and conservation',
            'healthcare_access': 'healthcare accessibility and quality',
            'social_equality': 'social equality and justice',
            'mental_wellness': 'mental health awareness and support',
            'community_building': 'community strengthening and connection',
            'innovation_advancement': 'technological advancement and innovation',
            'cultural_preservation': 'cultural preservation and celebration',
            'economic_opportunity': 'economic empowerment and opportunity',
            'youth_development': 'youth empowerment and development',
            'sustainable_living': 'sustainable living practices',
            'global_connection': 'global understanding and cooperation'
        }
    }

    def get_description(items, context):
        """Get natural descriptions for items in a specific context."""
        if not items:
            return ""
        phrases = []
        for item in items:
            phrase = context_phrases.get(context, {}).get(item, item.replace('_', ' '))
            if phrase not in phrases:
                phrases.append(phrase)
        return phrases

    # Prepare components for the statement
    talents_skills = format_list_naturally(
        get_description(talents[:2], 'talent') + 
        get_description(skills[:2], 'skill')
    )
    
    impact_phrases = get_description(impact_areas[:2], 'impact')
    impact = format_list_naturally(impact_phrases)
    
    passions_all = get_description(passions, 'passion')
    passions_primary = passions_all[0] if passions_all else ""
    passions_secondary = format_list_naturally(passions_all[1:2])
    passions_additional = format_list_naturally(passions_all[2:4])
    
    impact_additional = format_list_naturally(get_description(impact_areas[2:], 'impact'))

    # Select and fill template
    import random
    template = random.choice(templates)
    
    # Fill in the template
    statement = template.format(
        talents_skills=talents_skills,
        impact=impact,
        passions_primary=passions_primary,
        passions_secondary=passions_secondary,
        passions_additional=passions_additional,
        impact_additional=impact_additional or "create positive change in these areas"
    )
    
    return statement

def get_activity_descriptions(selected_items, category):
    """Generate detailed descriptions for selected activities."""
    activity_details = {
        'helping others': [
            'Volunteering to support communities or individuals in need',
            'Mentoring or coaching others to achieve their goals',
            'Participating in initiatives that uplift the underprivileged'
        ],
        'learning growth': [
            'Pursuing new skills that challenge your intellect',
            'Attending workshops and classes to expand knowledge',
            'Setting and achieving personal growth goals'
        ],
        'exploring': [
            'Discovering new perspectives and cultural experiences',
            'Trying innovative approaches to solving problems',
            'Investigating unexplored possibilities in your field'
        ],
        'leading others': [
            'Guiding teams toward achieving shared visions',
            'Inspiring others through leadership and example',
            'Organizing projects that bring people together'
        ],
        'analyzing data': [
            'Uncovering insights from complex information',
            'Solving intricate puzzles and challenges',
            'Conducting research to answer difficult questions'
        ],
        'creative expression': [
            'Creating content that inspires and educates',
            'Designing innovative solutions to problems',
            'Expressing ideas through various creative mediums'
        ],
        'technology': [
            'Exploring cutting-edge tools and technologies',
            'Developing solutions that enhance efficiency',
            'Bridging creativity and technical innovation'
        ],
        'education learning': [
            'Sharing knowledge through teaching and mentoring',
            'Creating engaging educational content',
            'Facilitating discussions that expand perspectives'
        ],
        'spirituality philosophy': [
            'Exploring questions of meaning and purpose',
            'Engaging in deep philosophical discussions',
            'Practicing mindfulness and self-reflection'
        ],
        'rapid learning': [
            'Quickly mastering new concepts and skills',
            'Adapting to changing environments effectively',
            'Synthesizing information from various sources'
        ],
        'idea generation': [
            'Creating innovative solutions to challenges',
            'Brainstorming new approaches to problems',
            'Connecting different concepts in unique ways'
        ],
        'systems thinking': [
            'Understanding complex interconnections',
            'Analyzing how different parts work together',
            'Designing comprehensive solutions'
        ],
        'people insight': [
            'Understanding others needs and motivations',
            'Building meaningful relationships',
            'Fostering positive team dynamics'
        ],
        'clear speaking': [
            'Communicating complex ideas clearly',
            'Presenting information effectively',
            'Facilitating productive discussions'
        ]
    }

    descriptions = []
    for item in selected_items:
        if item in activity_details:
            descriptions.append({
                'title': item.replace('_', ' ').title(),
                'details': activity_details[item]
            })
    
    return descriptions

def get_talent_descriptions(selected_items):
    """Generate detailed descriptions for natural talents and strengths."""
    talent_details = {
        'rapid learning': [
            'Quickly grasping complex concepts and new information',
            'Adapting knowledge from one field to solve problems in another',
            'Building on existing skills to master new challenges'
        ],
        'idea generation': [
            'Consistently producing innovative solutions to problems',
            'Seeing unique connections between different concepts',
            'Generating creative approaches to challenges'
        ],
        'systems thinking': [
            'Understanding how different parts of a system interact',
            'Identifying patterns and relationships in complex situations',
            'Anticipating the ripple effects of changes in a system'
        ],
        'people insight': [
            'Reading and understanding others emotional states',
            'Building rapport and trust naturally in relationships',
            'Sensing underlying motivations and needs'
        ],
        'physical grace': [
            'Moving with natural coordination and balance',
            'Expressing ideas through physical movement',
            'Learning new physical skills with ease'
        ],
        'clear speaking': [
            'Articulating complex ideas in accessible ways',
            'Adapting communication style to different audiences',
            'Using storytelling to make points memorable'
        ],
        'pattern recognition': [
            'Quickly identifying trends and relationships in data',
            'Spotting inconsistencies and potential problems',
            'Making accurate predictions based on observed patterns'
        ],
        'musical sense': [
            'Understanding rhythm and musical structure intuitively',
            'Recognizing subtle variations in tone and pitch',
            'Processing and remembering musical patterns easily'
        ],
        'social connection': [
            'Creating meaningful bonds with diverse groups of people',
            'Fostering positive group dynamics naturally',
            'Understanding and navigating social situations effectively'
        ],
        'future planning': [
            'Visualizing and mapping out long-term strategies',
            'Anticipating potential obstacles and preparing solutions',
            'Breaking down big goals into actionable steps'
        ],
        'tech intuition': [
            'Understanding new technologies quickly and naturally',
            'Seeing innovative ways to apply technical solutions',
            'Adapting easily to technological changes'
        ],
        'bounce back': [
            'Recovering quickly from setbacks and challenges',
            'Learning valuable lessons from difficult experiences',
            'Maintaining optimism in the face of obstacles'
        ],
        'natural curiosity': [
            'Constantly seeking to understand how things work',
            'Asking insightful questions that reveal new perspectives',
            'Exploring topics deeply and thoroughly'
        ],
        'deep empathy': [
            'Understanding and sharing others emotional experiences',
            'Offering meaningful support during difficult times',
            'Creating safe spaces for authentic expression'
        ],
        'quick adapting': [
            'Thriving in changing environments and situations',
            'Adjusting strategies based on new information',
            'Finding opportunities in unexpected circumstances'
        ],
        'goal pursuit': [
            'Maintaining focus on long-term objectives',
            'Persisting through challenges with determination',
            'Inspiring others to achieve their goals'
        ],
        'creative vision': [
            'Imagining innovative possibilities for the future',
            'Seeing potential where others see obstacles',
            'Developing unique solutions to common problems'
        ],
        'logical analysis': [
            'Breaking down complex problems methodically',
            'Evaluating situations objectively and clearly',
            'Finding efficient solutions through systematic thinking'
        ],
        'inner wisdom': [
            'Making decisions based on deep personal insight',
            'Trusting and following internal guidance',
            'Understanding subtle aspects of situations'
        ],
        'natural order': [
            'Creating systems that enhance efficiency',
            'Organizing information and resources effectively',
            'Bringing clarity to complex situations'
        ],
        'natural leading': [
            'Inspiring others to achieve their best',
            'Building and guiding effective teams',
            'Making decisions that benefit the group'
        ],
        'clear expression': [
            'Communicating ideas with precision and impact',
            'Helping others understand complex concepts',
            'Creating compelling narratives and presentations'
        ],
        'solution finding': [
            'Identifying creative ways to overcome obstacles',
            'Approaching problems from multiple angles',
            'Developing practical solutions to challenges'
        ]
    }

    descriptions = []
    for item in selected_items:
        if item in talent_details:
            descriptions.append({
                'title': item.title(),
                'details': talent_details[item]
            })
    
    return descriptions

def get_learning_resources(selected_items):
    """Generate curated learning resources based on selected interests and skills."""
    
    # Comprehensive mapping of learning resources
    learning_resources = {
        'creative_expression': [
            {'name': 'Coursera - Creativity & Innovation', 'url': 'https://www.coursera.org/specializations/creativity-innovation'},
            {'name': 'Skillshare - Creative Writing', 'url': 'https://www.skillshare.com/browse/creative-writing'},
            {'name': 'Udemy - Digital Art Fundamentals', 'url': 'https://www.udemy.com/topic/digital-art/'}
        ],
        'problem_solving': [
            {'name': 'edX - Critical Thinking & Problem Solving', 'url': 'https://www.edx.org/learn/critical-thinking'},
            {'name': 'Coursera - Problem-Solving Skills', 'url': 'https://www.coursera.org/learn/problem-solving'},
            {'name': 'LinkedIn Learning - Problem-Solving Techniques', 'url': 'https://www.linkedin.com/learning/topics/problem-solving'}
        ],
        'helping_others': [
            {'name': 'Coursera - Social Work Practice', 'url': 'https://www.coursera.org/learn/social-work-practice'},
            {'name': 'edX - Introduction to Psychology', 'url': 'https://www.edx.org/learn/psychology'},
            {'name': 'Udemy - Life Coaching Certification', 'url': 'https://www.udemy.com/topic/life-coaching/'}
        ],
        'learning_growth': [
            {'name': 'Coursera - Learning How to Learn', 'url': 'https://www.coursera.org/learn/learning-how-to-learn'},
            {'name': 'edX - The Science of Learning', 'url': 'https://www.edx.org/learn/education'},
            {'name': 'Mindvalley - Super Learning', 'url': 'https://www.mindvalley.com/superlearning'}
        ],
        'technology': [
            {'name': 'freeCodeCamp - Web Development', 'url': 'https://www.freecodecamp.org/'},
            {'name': 'The Odin Project - Full Stack Development', 'url': 'https://www.theodinproject.com/'},
            {'name': 'Codecademy - Programming Courses', 'url': 'https://www.codecademy.com/'}
        ],
        'education_learning': [
            {'name': 'Coursera - Teaching Excellence Program', 'url': 'https://www.coursera.org/professional-certificates/teaching'},
            {'name': 'edX - Educational Technology', 'url': 'https://www.edx.org/learn/education-technology'},
            {'name': 'LinkedIn Learning - Training & Development', 'url': 'https://www.linkedin.com/learning/topics/training-and-development'}
        ],
        'nature_environment': [
            {'name': 'Coursera - Environmental Science', 'url': 'https://www.coursera.org/browse/physical-science-and-engineering/environmental-science'},
            {'name': 'edX - Sustainable Development', 'url': 'https://www.edx.org/learn/sustainable-development'},
            {'name': 'National Geographic - Environmental Courses', 'url': 'https://www.nationalgeographic.com/education'}
        ],
        'business_entrepreneurship': [
            {'name': 'Y Combinator - Startup School', 'url': 'https://www.startupschool.org/'},
            {'name': 'Coursera - Business Foundations', 'url': 'https://www.coursera.org/specializations/wharton-business-foundations'},
            {'name': 'edX - Entrepreneurship Program', 'url': 'https://www.edx.org/learn/entrepreneurship'}
        ],
        'leadership': [
            {'name': 'Coursera - Strategic Leadership', 'url': 'https://www.coursera.org/specializations/strategic-leadership'},
            {'name': 'Harvard Online - Leadership Principles', 'url': 'https://online.hbs.edu/courses/leadership-principles/'},
            {'name': 'LinkedIn Learning - Leadership Development', 'url': 'https://www.linkedin.com/learning/topics/leadership-and-management'}
        ],
        'communication': [
            {'name': 'Coursera - Business Communication', 'url': 'https://www.coursera.org/specializations/improve-english'},
            {'name': 'edX - Public Speaking', 'url': 'https://www.edx.org/learn/public-speaking'},
            {'name': 'Toastmasters International', 'url': 'https://www.toastmasters.org/'}
        ]
    }
    
    # Collect relevant resources
    curated_resources = []
    seen_resources = set()  # To avoid duplicates
    
    for item in selected_items:
        if item in learning_resources:
            for resource in learning_resources[item]:
                # Use URL as unique identifier
                if resource['url'] not in seen_resources:
                    curated_resources.append({
                        'category': item.replace('_', ' ').title(),
                        'name': resource['name'],
                        'url': resource['url']
                    })
                    seen_resources.add(resource['url'])
    
    # Group resources by category
    categorized_resources = {}
    for resource in curated_resources:
        category = resource['category']
        if category not in categorized_resources:
            categorized_resources[category] = []
        categorized_resources[category].append({
            'name': resource['name'],
            'url': resource['url']
        })
    
    return categorized_resources

def generate_career_recommendations(selected_items):
    career_paths = {
        'creative_expression': [
            'Content Creator',
            'Creative Director',
            'Art Director',
            'Professional Writer',
            'Brand Strategist'
        ],
        'problem_solving': [
            'Management Consultant',
            'Data Scientist',
            'Software Engineer',
            'Business Analyst',
            'Research Scientist'
        ],
        'helping_others': [
            'Counselor or Therapist',
            'Social Worker',
            'Career Coach',
            'Healthcare Professional',
            'Nonprofit Director'
        ],
        'learning_growth': [
            'Education Administrator',
            'Corporate Trainer',
            'Curriculum Developer',
            'Learning Experience Designer',
            'Educational Consultant'
        ],
        'physical_activity': [
            'Physical Therapist',
            'Personal Trainer',
            'Sports Coach',
            'Wellness Program Director',
            'Movement Therapist'
        ],
        'building_things': [
            'Architect',
            'Product Designer',
            'Construction Manager',
            'Industrial Designer',
            'Mechanical Engineer'
        ],
        'organizing': [
            'Project Manager',
            'Operations Director',
            'Event Planner',
            'Logistics Coordinator',
            'Business Operations Manager'
        ],
        'communicating': [
            'Communications Director',
            'Public Relations Manager',
            'Marketing Manager',
            'Community Engagement Specialist',
            'Corporate Communications Manager'
        ],
        'exploring': [
            'Research Scientist',
            'Travel Writer',
            'Environmental Scientist',
            'Cultural Anthropologist',
            'Innovation Consultant'
        ],
        'leading_others': [
            'Executive Director',
            'Team Leader',
            'Department Head',
            'Program Manager',
            'Business Development Director'
        ],
        'analyzing_data': [
            'Data Analyst',
            'Business Intelligence Manager',
            'Market Research Analyst',
            'Financial Analyst',
            'Research Director'
        ],
        'performing': [
            'Professional Speaker',
            'Training Facilitator',
            'Performance Artist',
            'Theater Director',
            'Media Producer'
        ]
    }

    recommended_careers = []
    for item in selected_items:
        if item in career_paths:
            recommended_careers.extend(career_paths[item])
    
    # Remove duplicates and return top recommendations
    return list(set(recommended_careers))[:5]

if __name__ == '__main__':
    app.run(port=8085, debug=True)
