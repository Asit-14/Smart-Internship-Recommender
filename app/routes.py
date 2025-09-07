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
    """
    Process form submission.
    Following the flow:
    1. Collect form input
    2. Validate input
    3. Generate recommendations using the integrated process
    4. Format and display recommendations
    """
    try:
        # Collect form data
        form_data = {
            'skills': request.form.getlist('skills'),
            'sector': request.form.get('sector'),
            'location': request.form.get('location'),
            'education': request.form.get('education')
        }
        
        print(f"Form data received: sector='{form_data['sector']}', skills={form_data['skills']}, location='{form_data['location']}'")
        
        # Validate form data
        if not form_data['skills'] and not form_data['sector'] and not form_data['location']:
            flash('Please provide at least one skill, sector, or location preference.', 'warning')
            return redirect(url_for('main.index'))
        
        # Store form data in session for later use
        session['form_data'] = form_data
        
        # Get recommendations using the integrated process
        recommendations = service.integrated_recommendation_process(form_data, input_type='form')
        
        if not recommendations:
            flash('No matching internships found. Please try different criteria.', 'warning')
            return redirect(url_for('main.index'))
        
        # Format recommendations for the session
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
        
        print(f"Form submission processed, {len(recommendations)} recommendations found")
        return redirect(url_for('main.recommendations'))
    except Exception as e:
        print(f"Error processing form submission: {e}")
        flash('An error occurred while processing your preferences. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main.route('/resume-submit', methods=['POST'])
def resume_submit():
    """
    Process resume submission.
    Following the flow:
    1. Resume Upload
    2. File Validation
    3. Resume Parsing
    4. Candidate Profile Creation
    5. Recommendation Generation
    """
    try:
        # Check if resume file exists in the request
        if 'resume' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('main.index'))
        
        file = request.files['resume']
        
        # Check if file was selected
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('main.index'))
        
        # Validate file type
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
                
                # Use integrated recommendation process
                print(f"Resume data before recommendation: skills={len(resume_data.get('skills', []))}, locations={resume_data.get('locations', [])}")
                recommendations = service.integrated_recommendation_process(resume_data, input_type='resume')
                print(f"Recommendations returned: {len(recommendations) if recommendations else 0}")
                
                if not recommendations:
                    print("No recommendations found, redirecting to index with warning")
                    flash('No matching internships found. Try uploading a different resume or filling out the form.', 'warning')
                    return redirect(url_for('main.index'))
                
                # Format recommendations for the session
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
                
                print(f"Resume processed successfully, found {len(recommendations)} recommendations")
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
    """
    Render the recommendations page.
    Following the flow:
    1. Retrieve recommendations
    2. Format for display
    3. Show recommendations with career paths and skill development resources
    """
    try:
        # Get recommendations from session
        recommendations = session.get('recommendations', [])
        
        if not recommendations:
            flash('No recommendations found. Please fill out the form or upload a resume.', 'warning')
            return redirect(url_for('main.index'))
        
        # Validate and process recommendations for display
        valid_recommendations = []
        for rec in recommendations:
            if isinstance(rec, dict) and 'title' in rec and 'description' in rec:
                # Add any additional processing here if needed
                valid_recommendations.append(rec)
        
        if not valid_recommendations:
            flash('Invalid recommendation data. Please try again.', 'warning')
            return redirect(url_for('main.index'))
        
        print(f"Displaying {len(valid_recommendations)} recommendations")
        
        # Render template with recommendations
        return render_template('recommendations.html', recommendations=valid_recommendations)
    except Exception as e:
        print(f"Error displaying recommendations: {e}")
        flash('Error displaying recommendations. Please try again.', 'error')
        return redirect(url_for('main.index'))

def allowed_file(filename):
    """Check if the file type is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint for API calls.
    Accepts user profile data and returns top internship recommendations.
    """
    try:
        # Get data from request
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
            # Handle multiple values for skills
            if 'skills' in request.form:
                data['skills'] = request.form.getlist('skills')
        
        # Validate required fields
        if not any([data.get('skills'), data.get('sector'), data.get('location'), data.get('education')]):
            return jsonify({'error': 'Please provide at least one preference (skills, sector, location, or education)'}), 400
        
        # Get recommendations using the service
        recommendations = service.get_top_matches(data, top_n=5)
        
        if not recommendations:
            return jsonify({'message': 'No matching internships found', 'recommendations': []}), 200
        
        # Format response
        response_data = {
            'recommendations': [
                {
                    'id': rec['internship'].get('ID', ''),
                    'title': rec['internship'].get('Title', ''),
                    'organization': rec['internship'].get('Organization', ''),
                    'sector': rec['internship'].get('Sector', ''),
                    'location': rec['internship'].get('Location', ''),
                    'duration': rec['internship'].get('Duration', ''),
                    'stipend': rec['internship'].get('Stipend', ''),
                    'description': rec['internship'].get('Description', ''),
                    'skills_required': rec['internship'].get('Skills_Required', ''),
                    'apply_url': rec['internship'].get('Apply_URL', '#'),
                    'score': rec.get('score', 0),
                    'reason': rec.get('reason', ''),
                    'missing_skills': rec.get('missing_skills', []),
                    'career_path': rec.get('career_path'),
                    'learning_resources': rec.get('learning_resources', [])
                }
                for rec in recommendations
            ],
            'total_found': len(recommendations)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@main.route('/debug/resume-test', methods=['GET', 'POST'])
def debug_resume_test():
    """Debug endpoint to test resume processing"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file and allowed_file(file.filename):
            try:
                resume_data = service.process_resume(file)
                return jsonify({
                    'success': True,
                    'resume_data': resume_data,
                    'skills_count': len(resume_data.get('skills', [])),
                    'education_count': len(resume_data.get('education', [])),
                    'locations_count': len(resume_data.get('locations', []))
                })
            except Exception as e:
                return jsonify({'error': f'Resume processing error: {str(e)}'})
        
        return jsonify({'error': 'Invalid file type'})
    
    return '''
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="resume" accept=".pdf,.docx">
        <input type="submit" value="Test Resume Processing">
    </form>
    '''

def search():
    """
    Search internships by query and filters.
    """
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.json
            else:
                data = request.form.to_dict()
        else:
            data = request.args.to_dict()
        
        query = data.get('query', '')
        filters = {
            'sector': data.get('sector', ''),
            'location': data.get('location', ''),
            'education': data.get('education', '')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        # Search internships
        results = service.search_internships(query, filters)
        
        if request.is_json or request.method == 'POST':
            return jsonify({
                'results': results,
                'total_found': len(results),
                'query': query,
                'filters': filters
            })
        else:
            # Render search results page
            return render_template('search_results.html', 
                                 results=results, 
                                 query=query, 
                                 filters=filters,
                                 sectors=service.get_all_sectors(),
                                 locations=service.get_all_locations(),
                                 education=service.get_all_education())
    
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Search error: {e}', 'error')
            return redirect(url_for('main.index'))

@main.route('/internship/<internship_id>')
def internship_details(internship_id):
    """
    Get details of a specific internship.
    """
    try:
        internship = service.get_internship_by_id(internship_id)
        
        if not internship:
            if request.is_json:
                return jsonify({'error': 'Internship not found'}), 404
            else:
                flash('Internship not found', 'error')
                return redirect(url_for('main.index'))
        
        if request.is_json:
            return jsonify(internship)
        else:
            return render_template('internship_details.html', internship=internship)
    
    except Exception as e:
        print(f"Error getting internship details: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error loading internship details: {e}', 'error')
            return redirect(url_for('main.index'))

@main.route('/feedback', methods=['POST'])
def feedback():
    """
    Handle user feedback on recommendations.
    """
    try:
        if request.is_json:
            feedback_data = request.json
        else:
            feedback_data = request.form.to_dict()
        
        # Store feedback (in a real app, this would go to a database)
        success = service.store_feedback(feedback_data)
        
        if request.is_json:
            return jsonify({'success': success, 'message': 'Feedback received'})
        else:
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('main.recommendations'))
    
    except Exception as e:
        print(f"Error handling feedback: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash('Error submitting feedback', 'error')
            return redirect(url_for('main.recommendations'))

@main.route('/api/data/reload', methods=['POST'])
def reload_data():
    """
    Reload internship data from CSV files (admin endpoint).
    """
    try:
        success = service.load_internship_data()
        return jsonify({
            'success': success,
            'message': 'Data reloaded successfully' if success else 'Failed to reload data'
        })
    except Exception as e:
        print(f"Error reloading data: {e}")
        return jsonify({'error': str(e)}), 500
