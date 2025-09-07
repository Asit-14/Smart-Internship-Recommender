import pandas as pd
import os
from models.recommender import get_recommendations, get_career_path, get_learning_resources
from utils.resume_parser import parse_resume
import tempfile

class InternshipService:
    """
    Internship Service class that handles the core functionality of the Smart Internship Recommender.
    Based on the system architecture diagram:
    1. User input collection (form, resume, voice)
    2. Data processing and analysis
    3. Recommendation generation
    4. Career path planning and skill development suggestions
    """
    def __init__(self, data_dir='data'):
        """Initialize the internship service with data files"""
        self.data_dir = data_dir
        
        # Load all necessary data files
        try:
            self.internships_df = pd.read_csv(os.path.join(data_dir, 'internships.csv'))
            self.skills_df = pd.read_csv(os.path.join(data_dir, 'skills.csv'))
            self.locations_df = pd.read_csv(os.path.join(data_dir, 'locations.csv'))
            self.education_df = pd.read_csv(os.path.join(data_dir, 'education.csv'))
            self.sectors_df = pd.read_csv(os.path.join(data_dir, 'sectors.csv'))
            self.career_paths_df = pd.read_csv(os.path.join(data_dir, 'career_paths.csv'))
            self.learning_resources_df = pd.read_csv(os.path.join(data_dir, 'learning_resources.csv'))
            print(f"Successfully loaded all data files from {data_dir}")
        except Exception as e:
            print(f"Error loading data files: {e}")
            raise
    
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
        """
        Process the resume file and extract information
        Following the process flow:
        1. Upload Resume
        2. Parse Resume
        3. Extract Skills, Education, Location
        4. Build Candidate Profile
        """
        print("Starting resume processing")
        
        # Default resume data if anything fails
        default_resume_data = {
            'skills': [],
            'education': [],
            'locations': [],
            'full_text': ""
        }
        
        # Step 1: Validate Resume File
        if not resume_file or not hasattr(resume_file, 'filename') or not resume_file.filename:
            print("Error: Invalid resume file")
            return default_resume_data
            
        # Only process PDF and DOCX files
        if not (resume_file.filename.lower().endswith('.pdf') or resume_file.filename.lower().endswith('.docx')):
            print(f"Error: Unsupported file format: {resume_file.filename}")
            return default_resume_data
        
        try:
            print(f"Processing resume: {resume_file.filename}")
            
            # Step 2: Save the uploaded file to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, resume_file.filename)
            resume_file.save(temp_file_path)
            
            # Check if file was saved successfully
            if not os.path.exists(temp_file_path):
                print(f"Error: Failed to save temporary file: {temp_file_path}")
                return default_resume_data
                
            # Step 3: Parse the resume and extract information
            print("Parsing resume content")
            resume_data = parse_resume(temp_file_path, self.skills_df, self.education_df, self.locations_df)
            
            # Step 4: Clean up - Remove the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
            
            # Print a summary of what was extracted
            skills_count = len(resume_data.get('skills', []))
            education_count = len(resume_data.get('education', []))
            locations_count = len(resume_data.get('locations', []))
            
            print(f"Resume processed successfully. Extracted {skills_count} skills, "
                  f"{education_count} education items, and {locations_count} locations")
            
            return resume_data
            
        except Exception as e:
            print(f"Error processing resume: {e}")
            return default_resume_data
    
    def get_recommendations_from_form(self, form_data):
        """
        Get internship recommendations based on form data
        Following the process flow:
        1. Input Collection (form data)
        2. Data Preprocessing 
        3. Candidate Profile Analysis
        4. Recommendation Generation
        5. Career Path Planning and Skill Development
        """
        try:
            print("Starting form-based recommendation process")
            
            # Step 1: Input Validation
            if not isinstance(form_data, dict):
                print(f"Error: form_data is not a dictionary: {form_data}")
                return []
            
            # Step 2: Data Preprocessing - Create candidate profile
            candidate = {
                'skills': form_data.get('skills', []),
                'sector': form_data.get('sector', ''),
                'location': form_data.get('location', ''),
                'education': form_data.get('education', ''),
                'full_text': ''  # No resume text for form-based input
            }
            
            print(f"Processing candidate profile with {len(candidate['skills'])} skills, " 
                  f"sector: {candidate['sector']}, location: {candidate['location']}")
            
            # Step 3: Generate Recommendations
            try:
                recommendations = get_recommendations(candidate, self.internships_df, self.locations_df)
                print(f"Generated {len(recommendations)} initial recommendations")
            except Exception as e:
                print(f"Error getting recommendations from form data: {e}")
                return []
            
            # Step 4: Enhance with Career Path and Learning Resources
            enhanced_recommendations = []
            for recommendation in recommendations:
                try:
                    missing_skills = recommendation.get('missing_skills', [])
                    print(f"Found {len(missing_skills)} missing skills for internship: {recommendation['internship'].get('Title')}")
                    
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
                    
                    enhanced_recommendations.append(recommendation)
                except Exception as e:
                    print(f"Error enhancing recommendation: {e}")
                    recommendation['learning_resources'] = []
                    recommendation['career_path'] = None
                    enhanced_recommendations.append(recommendation)
            
            print(f"Returning {len(enhanced_recommendations)} enhanced recommendations")
            return enhanced_recommendations
        except Exception as e:
            print(f"Error processing form data: {e}")
            return []
    
    def get_recommendations_from_resume(self, resume_data):
        """
        Get internship recommendations based on resume data
        Following the process flow:
        1. Resume Data Analysis
        2. Candidate Profile Creation
        3. Recommendation Generation
        4. Career Path Planning
        5. Skill Development Suggestions
        """
        try:
            print("Starting resume-based recommendation process")
            
            # Step 1: Validate resume data
            if not isinstance(resume_data, dict):
                print(f"Error: resume_data is not a dictionary: {resume_data}")
                return []
                
            # Step 2: Build candidate profile from resume data
            # Set default values for missing keys
            default_resume_data = {
                'skills': [],
                'sector': '',
                'location': '',
                'education': '',
                'full_text': ''
            }
            
            # Create candidate profile with resume data
            candidate = {}
            for key, default_value in default_resume_data.items():
                candidate[key] = resume_data.get(key, default_value)
                
            # If location is a list (from resume parsing), use the first one
            if isinstance(candidate['location'], list) and len(candidate['location']) > 0:
                candidate['location'] = candidate['location'][0]
                
            # If education is a list (from resume parsing), use the highest one
            if isinstance(candidate['education'], list) and len(candidate['education']) > 0:
                candidate['education'] = candidate['education'][0]
            
            print(f"Built candidate profile with {len(candidate['skills'])} skills, "
                  f"location: {candidate['location']}, education: {candidate['education']}")
            
            # Step 3: Generate initial recommendations
            try:
                recommendations = get_recommendations(candidate, self.internships_df, self.locations_df)
                print(f"Generated {len(recommendations)} initial recommendations")
            except Exception as e:
                print(f"Error getting recommendations from resume data: {e}")
                return []
            
            # Step 4: Enhance recommendations with career paths and learning resources
            enhanced_recommendations = []
            for recommendation in recommendations:
                try:
                    # Identify skill gaps
                    missing_skills = recommendation.get('missing_skills', [])
                    print(f"Found {len(missing_skills)} missing skills for internship: {recommendation['internship'].get('Title')}")
                    
                    # Get learning resources for missing skills
                    recommendation['learning_resources'] = get_learning_resources(
                        missing_skills, 
                        self.learning_resources_df
                    )
                    
                    # Get career path based on the internship's sector
                    recommendation['career_path'] = get_career_path(
                        recommendation['internship']['Sector'], 
                        candidate['skills'],
                        self.career_paths_df
                    )
                    
                    enhanced_recommendations.append(recommendation)
                except Exception as e:
                    print(f"Error enhancing recommendation: {e}")
                    recommendation['learning_resources'] = []
                    recommendation['career_path'] = None
                    enhanced_recommendations.append(recommendation)
            
            print(f"Returning {len(enhanced_recommendations)} enhanced recommendations")
            return enhanced_recommendations
        except Exception as e:
            print(f"Error processing resume data: {e}")
            return []

    def integrated_recommendation_process(self, input_data, input_type='form'):
        """
        Integrated recommendation process that follows the complete system flow diagram
        
        Parameters:
        - input_data: The input data (form, resume, or voice)
        - input_type: Type of input ('form', 'resume', 'voice')
        
        Flow:
        1. Input Collection & Processing
        2. Candidate Profile Creation
        3. Internship Matching & Scoring
        4. Skill Gap Analysis
        5. Career Path Planning
        6. Learning Resource Recommendations
        7. Final Recommendation Generation
        """
        try:
            print(f"Starting integrated recommendation process with input_type: {input_type}")
            
            # Step 1: Process input based on type
            candidate = {}
            if input_type == 'form':
                candidate = {
                    'skills': input_data.get('skills', []),
                    'sector': input_data.get('sector', ''),
                    'location': input_data.get('location', ''),
                    'education': input_data.get('education', ''),
                    'full_text': ''
                }
            elif input_type == 'resume':
                # Extract from resume data
                locations_list = input_data.get('locations', [])
                education_list = input_data.get('education', [])
                
                candidate = {
                    'skills': input_data.get('skills', []),
                    'sector': input_data.get('sector', ''),
                    'location': locations_list[0] if locations_list and len(locations_list) > 0 else '',
                    'education': education_list[0] if education_list and len(education_list) > 0 else '',
                    'full_text': input_data.get('full_text', '')
                }
            
            print(f"Candidate profile created with {len(candidate.get('skills', []))} skills")
            
            # Step 2: Generate recommendations
            raw_recommendations = get_recommendations(candidate, self.internships_df, self.locations_df)
            print(f"Generated {len(raw_recommendations)} initial recommendations")
            
            # Step 3: Enhance recommendations with career paths and learning resources
            enhanced_recommendations = []
            for rec in raw_recommendations:
                # Skill gap analysis
                missing_skills = rec.get('missing_skills', [])
                
                # Add learning resources
                rec['learning_resources'] = get_learning_resources(
                    missing_skills, 
                    self.learning_resources_df
                )
                
                # Add career path
                rec['career_path'] = get_career_path(
                    rec['internship']['Sector'], 
                    candidate['skills'],
                    self.career_paths_df
                )
                
                enhanced_recommendations.append(rec)
            
            print(f"Enhanced and returning {len(enhanced_recommendations)} recommendations")
            return enhanced_recommendations
            
        except Exception as e:
            print(f"Error in integrated recommendation process: {e}")
            return []
    
    def store_feedback(self, feedback_data):
        """Store user feedback for analytics"""
        # In a real application, this would store data to a database
        # For now, we'll just print it
        print(f"Feedback received: {feedback_data}")
        return True
    
    def get_top_matches(self, user_profile, top_n=5):
        """
        Get top matching internships for a user profile.
        This is the main matching function that integrates all recommendation logic.
        
        Args:
            user_profile (dict): User profile containing skills, education, sector, location
            top_n (int): Number of top recommendations to return
            
        Returns:
            list: Top matching internships with scores and explanations
        """
        try:
            print(f"Getting top {top_n} matches for user profile")
            
            # Use the integrated recommendation process
            recommendations = self.integrated_recommendation_process(user_profile, input_type='profile')
            
            # Return only the requested number of recommendations
            return recommendations[:top_n] if recommendations else []
            
        except Exception as e:
            print(f"Error getting top matches: {e}")
            return []
    
    def load_internship_data(self):
        """
        Reload internship data from CSV files.
        Useful for refreshing data without restarting the application.
        """
        try:
            self.internships_df = pd.read_csv(os.path.join(self.data_dir, 'internships.csv'))
            print(f"Reloaded {len(self.internships_df)} internships")
            return True
        except Exception as e:
            print(f"Error reloading internship data: {e}")
            return False
    
    def get_internship_by_id(self, internship_id):
        """
        Get a specific internship by its ID.
        
        Args:
            internship_id (str): The internship ID
            
        Returns:
            dict: Internship details or None if not found
        """
        try:
            internship = self.internships_df[self.internships_df['ID'] == str(internship_id)]
            if not internship.empty:
                return internship.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting internship by ID {internship_id}: {e}")
            return None
    
    def search_internships(self, query, filters=None):
        """
        Search internships by query and optional filters.
        
        Args:
            query (str): Search query
            filters (dict): Optional filters for sector, location, etc.
            
        Returns:
            list: Matching internships
        """
        try:
            df = self.internships_df.copy()
            
            # Apply filters if provided
            if filters:
                if 'sector' in filters and filters['sector']:
                    df = df[df['Sector'].str.contains(filters['sector'], case=False, na=False)]
                if 'location' in filters and filters['location']:
                    df = df[df['Location'].str.contains(filters['location'], case=False, na=False)]
                if 'education' in filters and filters['education']:
                    df = df[df['Education_Required'].str.contains(filters['education'], case=False, na=False)]
            
            # Search in title and description
            if query:
                query_mask = (
                    df['Title'].str.contains(query, case=False, na=False) |
                    df['Description'].str.contains(query, case=False, na=False) |
                    df['Skills_Required'].str.contains(query, case=False, na=False)
                )
                df = df[query_mask]
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Error searching internships: {e}")
            return []
