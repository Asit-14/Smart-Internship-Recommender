import pandas as pd
import os
from models.recommender import get_recommendations, get_career_path, get_learning_resources
from utils.resume_parser import parse_resume
import tempfile

class InternshipService:
    def __init__(self, data_dir='data'):
        """Initialize the internship service with data files"""
        self.data_dir = data_dir
        self.internships_df = pd.read_csv(os.path.join(data_dir, 'internships.csv'))
        self.skills_df = pd.read_csv(os.path.join(data_dir, 'skills.csv'))
        self.locations_df = pd.read_csv(os.path.join(data_dir, 'locations.csv'))
        self.education_df = pd.read_csv(os.path.join(data_dir, 'education.csv'))
        self.sectors_df = pd.read_csv(os.path.join(data_dir, 'sectors.csv'))
        self.career_paths_df = pd.read_csv(os.path.join(data_dir, 'career_paths.csv'))
        self.learning_resources_df = pd.read_csv(os.path.join(data_dir, 'learning_resources.csv'))
    
    def get_all_skills(self):
        """Get all skills from the skills database"""
        return self.skills_df['Skill'].tolist()
    
    def get_all_sectors(self):
        """Get all sectors from the sectors database"""
        return self.sectors_df['Sector'].tolist()
    
    def get_all_locations(self):
        """Get all locations from the locations database"""
        locations = []
        locations.extend(self.locations_df['State'].unique().tolist())
        locations.extend(self.locations_df['City'].tolist())
        return sorted(locations)
    
    def get_all_education(self):
        """Get all education categories"""
        return self.education_df['Category'].tolist()
    
    def process_resume(self, resume_file):
        """Process the resume file and extract information"""
        # Default resume data if anything fails
        default_resume_data = {
            'skills': [],
            'education': [],
            'locations': [],
            'full_text': ""
        }
        
        if not resume_file or not hasattr(resume_file, 'filename') or not resume_file.filename:
            print("Error: Invalid resume file")
            return default_resume_data
            
        # Only process PDF and DOCX files
        if not (resume_file.filename.lower().endswith('.pdf') or resume_file.filename.lower().endswith('.docx')):
            print(f"Error: Unsupported file format: {resume_file.filename}")
            return default_resume_data
        
        try:
            # Save the uploaded file to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, resume_file.filename)
            resume_file.save(temp_file_path)
            
            # Check if file was saved successfully
            if not os.path.exists(temp_file_path):
                print(f"Error: Failed to save temporary file: {temp_file_path}")
                return default_resume_data
                
            # Parse the resume
            resume_data = parse_resume(temp_file_path, self.skills_df, self.education_df, self.locations_df)
            
            # Remove the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
            
            return resume_data
            
        except Exception as e:
            print(f"Error processing resume: {e}")
            return default_resume_data
    
    def get_recommendations_from_form(self, form_data):
        """Get internship recommendations based on form data"""
        try:
            # Validate form_data
            if not isinstance(form_data, dict):
                print(f"Error: form_data is not a dictionary: {form_data}")
                return []
            
            candidate = {
                'skills': form_data.get('skills', []),
                'sector': form_data.get('sector', ''),
                'location': form_data.get('location', ''),
                'education': form_data.get('education', ''),
                'full_text': ''  # No resume text for form-based input
            }
            
            try:
                recommendations = get_recommendations(candidate, self.internships_df, self.locations_df)
            except Exception as e:
                print(f"Error getting recommendations from form data: {e}")
                return []
            
            # Enhance recommendations with career path and learning resources
            for recommendation in recommendations:
                try:
                    missing_skills = recommendation.get('missing_skills', [])
                    
                    # Get learning resources for missing skills
                    recommendation['learning_resources'] = get_learning_resources(
                        missing_skills, 
                        self.learning_resources_df
                    )
                    
                    # Get career path if sector is provided
                    recommendation['career_path'] = get_career_path(
                        recommendation['internship']['Sector'], 
                        candidate['skills'],
                        self.career_paths_df
                    )
                except Exception as e:
                    print(f"Error enhancing recommendation: {e}")
                    recommendation['learning_resources'] = []
                    recommendation['career_path'] = None
            
            return recommendations
        except Exception as e:
            print(f"Error processing form data: {e}")
            return []
    
    def get_recommendations_from_resume(self, resume_data):
        """Get internship recommendations based on resume data"""
        try:
            # Validate resume_data
            if not isinstance(resume_data, dict):
                print(f"Error: resume_data is not a dictionary: {resume_data}")
                return []
                
            # Set default values for missing keys
            default_resume_data = {
                'skills': [],
                'sector': '',
                'location': '',
                'education': '',
                'full_text': ''
            }
            
            # Update with actual values
            for key, default_value in default_resume_data.items():
                if key not in resume_data or resume_data[key] is None:
                    resume_data[key] = default_value
            
            try:
                recommendations = get_recommendations(resume_data, self.internships_df, self.locations_df)
            except Exception as e:
                print(f"Error getting recommendations from resume data: {e}")
                return []
            
            # Enhance recommendations with career path and learning resources
            for recommendation in recommendations:
                try:
                    missing_skills = recommendation.get('missing_skills', [])
                    
                    # Get learning resources for missing skills
                    recommendation['learning_resources'] = get_learning_resources(
                        missing_skills, 
                        self.learning_resources_df
                    )
                    
                    # Get career path based on the internship's sector
                    recommendation['career_path'] = get_career_path(
                        recommendation['internship']['Sector'], 
                        resume_data['skills'],
                        self.career_paths_df
                    )
                except Exception as e:
                    print(f"Error enhancing recommendation: {e}")
                    recommendation['learning_resources'] = []
                    recommendation['career_path'] = None
            
            return recommendations
        except Exception as e:
            print(f"Error processing resume data: {e}")
            return []
    
    def store_feedback(self, feedback_data):
        """Store user feedback for analytics"""
        # In a real application, this would store data to a database
        # For now, we'll just print it
        print(f"Feedback received: {feedback_data}")
        return True
