from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from services.internship_service import InternshipService
import json

# Create blueprint
main = Blueprint('main', __name__)

# Initialize service
service = InternshipService(data_dir='data')

@main.route('/', methods=['GET'])
def index():
    """Render the main page"""
    # Get data for dropdowns
    sectors = service.get_all_sectors()
    locations = service.get_all_locations()
    education = service.get_all_education()
    skills = service.get_all_skills()
    
    return render_template(
        'index.html',
        sectors=sectors,
        locations=locations,
        education=education,
        skills=skills
    )

@main.route('/form-submit', methods=['POST'])
def form_submit():
    """Process form submission"""
    try:
        form_data = {
            'skills': request.form.getlist('skills'),
            'sector': request.form.get('sector'),
            'location': request.form.get('location'),
            'education': request.form.get('education')
        }
        
        # Validate form data
        if not form_data['skills'] and not form_data['sector'] and not form_data['location']:
            flash('Please provide at least one skill, sector, or location preference.', 'warning')
            return redirect(url_for('main.index'))
        
        # Store form data in session for later use
        session['form_data'] = form_data
        
        # Get recommendations
        recommendations = service.get_recommendations_from_form(form_data)
        
        if not recommendations:
            flash('No matching internships found. Please try different criteria.', 'warning')
            return redirect(url_for('main.index'))
        
        # Store recommendations in session
        session['recommendations'] = [
            {
                'id': rec['internship'].get('ID', ''),
                'title': rec['internship'].get('Title', 'Internship'),
                'sector': rec['internship'].get('Sector', ''),
                'location': rec['internship'].get('Location', ''),
                'duration': rec['internship'].get('Duration', ''),
                'stipend': rec['internship'].get('Stipend', ''),
                'description': rec['internship'].get('Description', ''),
                'apply_url': rec['internship'].get('Apply_URL', '#'),
                'reason': rec.get('reason', 'This internship matches your profile'),
                'missing_skills': rec.get('missing_skills', []),
                'learning_resources': rec.get('learning_resources', []),
                'career_path': rec.get('career_path', None)
            }
            for rec in recommendations
        ]
        
        return redirect(url_for('main.recommendations'))
    except Exception as e:
        print(f"Error processing form submission: {e}")
        flash('An error occurred while processing your preferences. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main.route('/resume-submit', methods=['POST'])
def resume_submit():
    """Process resume submission"""
    try:
        if 'resume' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('main.index'))
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('main.index'))
        
        if file and allowed_file(file.filename):
            try:
                # Process the resume
                resume_data = service.process_resume(file)
                
                if not resume_data or not isinstance(resume_data, dict):
                    flash('Error processing resume. Please try again or fill out the form manually.', 'error')
                    return redirect(url_for('main.index'))
                
                # Store resume data in session for later use
                session['resume_data'] = {
                    'skills': resume_data.get('skills', []),
                    'education': resume_data.get('education', ''),
                    'locations': resume_data.get('locations', [])
                }
                
                # Get recommendations
                recommendations = service.get_recommendations_from_resume(resume_data)
                
                if not recommendations:
                    flash('No matching internships found. Try uploading a different resume or filling out the form.', 'warning')
                    return redirect(url_for('main.index'))
                
                # Store recommendations in session
                session['recommendations'] = [
                    {
                        'id': rec['internship'].get('ID', ''),
                        'title': rec['internship'].get('Title', 'Internship'),
                        'sector': rec['internship'].get('Sector', ''),
                        'location': rec['internship'].get('Location', ''),
                        'duration': rec['internship'].get('Duration', ''),
                        'stipend': rec['internship'].get('Stipend', ''),
                        'description': rec['internship'].get('Description', ''),
                        'apply_url': rec['internship'].get('Apply_URL', '#'),
                        'reason': rec.get('reason', 'This internship matches your profile'),
                        'missing_skills': rec.get('missing_skills', []),
                        'learning_resources': rec.get('learning_resources', []),
                        'career_path': rec.get('career_path', None)
                    }
                    for rec in recommendations
                ]
                
                return redirect(url_for('main.recommendations'))
            except Exception as e:
                print(f"Error processing resume: {e}")
                flash('Error analyzing resume. Please try again or fill out the form manually.', 'error')
                return redirect(url_for('main.index'))
        
        flash('Invalid file type. Please upload a PDF or DOCX file.', 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        print(f"Unexpected error in resume submission: {e}")
        flash('An unexpected error occurred. Please try again or contact support.', 'error')
        return redirect(url_for('main.index'))

@main.route('/recommendations', methods=['GET'])
def recommendations():
    """Render the recommendations page"""
    try:
        recommendations = session.get('recommendations', [])
        
        if not recommendations:
            flash('No recommendations found. Please fill out the form or upload a resume.', 'warning')
            return redirect(url_for('main.index'))
        
        # Validate that recommendations have the required structure
        valid_recommendations = []
        for rec in recommendations:
            if isinstance(rec, dict) and 'title' in rec and 'description' in rec:
                valid_recommendations.append(rec)
        
        if not valid_recommendations:
            flash('Invalid recommendation data. Please try again.', 'warning')
            return redirect(url_for('main.index'))
        
        return render_template('recommendations.html', recommendations=valid_recommendations)
    except Exception as e:
        print(f"Error displaying recommendations: {e}")
        flash('Error displaying recommendations. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main.route('/feedback', methods=['POST'])
def feedback():
    """Handle user feedback"""
    data = request.form
    
    # Store feedback
    service.store_feedback(data)
    
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('main.index'))

@main.route('/voice-input', methods=['POST'])
def voice_input():
    """Handle voice input and extract information from spoken text"""
    try:
        # Handle both JSON and form data for flexibility
        if request.is_json:
            text = request.json.get('text', '')
        else:
            text = request.form.get('voice_text', '')
            
        if not text:
            if request.is_json:
                return jsonify({'error': 'No speech text provided'}), 400
            else:
                flash('No speech text provided', 'error')
                return redirect(url_for('main.index'))
        
        print(f"Processing voice input: {text}")
        
        # Initialize service if needed
        sectors_df = service.sectors_df
        locations_df = service.locations_df
        skills_df = service.skills_df
        
        # Extract sector information
        sector = ''
        for idx, row in sectors_df.iterrows():
            sector_name = str(row['Category']).lower()
            if sector_name in text.lower():
                sector = row['Category']
                break
        
        # Extract location information
        location = ''
        for idx, row in locations_df.iterrows():
            # Check for city names
            city_name = str(row['City']).lower()
            if city_name in text.lower():
                location = row['City']
                break
            
            # Check for state names
            state_name = str(row['State']).lower()
            if state_name in text.lower():
                location = row['State']
                break
        
        # Extract skills
        skills = []
        for idx, row in skills_df.iterrows():
            skill_name = str(row['Skill']).lower()
            if skill_name in text.lower():
                skills.append(row['Skill'])
        
        # Add some common skills detection
        common_skills = {
            'programming': ['programming', 'coding', 'developer', 'software'],
            'writing': ['writing', 'content', 'article', 'blog'],
            'design': ['design', 'graphic', 'ui', 'ux', 'interface'],
            'data analysis': ['data', 'analysis', 'analytics', 'statistics'],
            'marketing': ['marketing', 'social media', 'digital marketing'],
            'teaching': ['teaching', 'education', 'tutoring', 'mentor']
        }
        
        for skill, keywords in common_skills.items():
            for keyword in keywords:
                if keyword in text.lower() and skill not in skills:
                    skills.append(skill)
                    break
        
        # Handle form submission directly if it's not a JSON request
        if not request.is_json:
            form_data = {
                'sector': sector,
                'location': location,
                'skills': skills,
                'education': 'Graduate'  # Default value
            }
            
            # Store form data in session
            session['form_data'] = form_data
            
            # Get recommendations
            recommendations = service.get_recommendations_from_form(form_data)
            
            if not recommendations:
                flash('No matching internships found. Please try different criteria.', 'warning')
                return redirect(url_for('main.index'))
            
            # Store recommendations in session
            session['recommendations'] = [
                {
                    'id': rec['internship'].get('ID', ''),
                    'title': rec['internship'].get('Title', 'Internship'),
                    'sector': rec['internship'].get('Sector', ''),
                    'location': rec['internship'].get('Location', ''),
                    'duration': rec['internship'].get('Duration', ''),
                    'stipend': rec['internship'].get('Stipend', ''),
                    'description': rec['internship'].get('Description', ''),
                    'apply_url': rec['internship'].get('Apply_URL', '#'),
                    'reason': rec.get('reason', 'This internship matches your profile'),
                    'missing_skills': rec.get('missing_skills', []),
                    'learning_resources': rec.get('learning_resources', []),
                    'career_path': rec.get('career_path', None)
                }
                for rec in recommendations
            ]
            
            return redirect(url_for('main.recommendations'))
        else:
            # Return JSON response for API/AJAX calls
            result = {
                'sector': sector,
                'location': location,
                'skills': skills,
                'text': text  # Return the original text for reference
            }
            
            return jsonify(result)
    except Exception as e:
        print(f"Error processing voice input: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error processing voice input: {e}', 'error')
            return redirect(url_for('main.index'))

def allowed_file(filename):
    """Check if the file type is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
