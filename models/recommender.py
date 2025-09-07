import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def preprocess_skills(skills_text):
    """Convert skills list to a standardized format"""
    # Handle None, NaN, or empty strings
    if skills_text is None or pd.isna(skills_text) or skills_text == "":
        return []
    
    # If it's already a list
    if isinstance(skills_text, list):
        return [skill.strip() for skill in skills_text if skill and not pd.isna(skill)]
    
    # If it's a string, split by commas
    try:
        skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
        return skills
    except (AttributeError, TypeError):
        print(f"Error processing skills: {skills_text} (type: {type(skills_text)})")
        return []

def calculate_skill_match(candidate_skills, internship_skills):
    """Calculate the skill match score between candidate and internship"""
    # Ensure we have valid input
    if candidate_skills is None:
        candidate_skills = []
    if internship_skills is None:
        internship_skills = []
    
    # Check if we have any skills to match
    if not candidate_skills or not internship_skills:
        return 0
    
    try:
        # Preprocess skills
        candidate_skills_processed = [skill.lower() for skill in preprocess_skills(candidate_skills) if skill]
        internship_skills_processed = [skill.lower() for skill in preprocess_skills(internship_skills) if skill]
        
        # Check if we have any processed skills
        if not candidate_skills_processed or not internship_skills_processed:
            return 0
            
        # Find common skills
        common_skills = set(candidate_skills_processed).intersection(set(internship_skills_processed))
        
        # Calculate score as ratio of matched skills to total internship skills
        if len(internship_skills_processed) == 0:
            return 0
        
        # Give more weight to matching a higher percentage of required skills
        return len(common_skills) / len(internship_skills_processed)
    except Exception as e:
        print(f"Error in skill matching: {e}")
        return 0

def calculate_sector_match(candidate_sector, internship_sector):
    """Calculate sector match between candidate and internship"""
    if pd.isna(candidate_sector) or pd.isna(internship_sector):
        return 0
    
    if candidate_sector.lower() == internship_sector.lower():
        return 1
    return 0

def calculate_location_match(candidate_location, internship_location, location_df):
    """Calculate location match between candidate and internship"""
    if pd.isna(candidate_location) or pd.isna(internship_location):
        return 0
    
    # Exact city match
    if candidate_location.lower() == internship_location.lower():
        return 1
    
    # Check if in same state
    candidate_state = None
    internship_state = None
    
    # Find state for candidate location (if it's a city)
    candidate_city_match = location_df[location_df['City'].str.lower() == candidate_location.lower()]
    if not candidate_city_match.empty:
        candidate_state = candidate_city_match['State'].iloc[0]
    else:
        # Check if the candidate location is directly a state
        if candidate_location in location_df['State'].values:
            candidate_state = candidate_location
    
    # Find state for internship location (if it's a city)
    internship_city_match = location_df[location_df['City'].str.lower() == internship_location.lower()]
    if not internship_city_match.empty:
        internship_state = internship_city_match['State'].iloc[0]
    else:
        # Check if the internship location is directly a state
        if internship_location in location_df['State'].values:
            internship_state = internship_location
    
    # If both are in the same state
    if candidate_state and internship_state and candidate_state == internship_state:
        return 0.5
    
    return 0

def calculate_text_similarity(candidate_text, internship_description):
    """Calculate text similarity between resume and internship description"""
    if pd.isna(candidate_text) or pd.isna(internship_description):
        return 0
    
    # Convert to string if not already
    candidate_text = str(candidate_text)
    internship_description = str(internship_description)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        # Create TF-IDF matrix
        tfidf_matrix = vectorizer.fit_transform([candidate_text, internship_description])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except Exception as e:
        print(f"Error calculating text similarity: {e}")
        return 0

def generate_reason(candidate, internship, scores):
    """Generate a reason for the recommendation"""
    reasons = []
    
    # Skill match reason
    if scores['skill_match'] > 0:
        # Find common skills
        candidate_skills = [skill.lower() for skill in preprocess_skills(candidate['skills'])]
        internship_skills = [skill.lower() for skill in preprocess_skills(internship['Skills_Required'])]
        common_skills = set(candidate_skills).intersection(set(internship_skills))
        
        if common_skills:
            top_skills = list(common_skills)[:3]  # Show at most 3 skills
            skills_text = ", ".join(top_skills)
            reasons.append(f"Your skills in {skills_text} match this internship's requirements.")
    
    # Sector match reason
    if scores['sector_match'] > 0:
        reasons.append(f"This internship is in the {internship['Sector']} sector, which matches your interest.")
    
    # Location match reason
    if scores['location_match'] > 0:
        reasons.append(f"This internship is located in {internship['Location']}, which matches your preferred location.")
    
    # If no specific reasons, give a general one based on text similarity
    if not reasons and scores['text_similarity'] > 0.1:
        reasons.append("Your profile shows a good match with this internship's description.")
    
    if not reasons:
        reasons.append("This is a popular internship in your selected area of interest.")
    
    return reasons[0]  # Return the first reason

def find_missing_skills(candidate_skills, internship_skills):
    """Find skills required by the internship that the candidate doesn't have"""
    # Ensure we have valid input
    if candidate_skills is None:
        candidate_skills = []
    if internship_skills is None:
        internship_skills = []
        
    try:
        # Preprocess skills
        candidate_skills_processed = [skill.lower() for skill in preprocess_skills(candidate_skills) if skill]
        internship_skills_processed = [skill.lower() for skill in preprocess_skills(internship_skills) if skill]
        
        # Find missing skills
        missing_skills = [skill for skill in internship_skills_processed 
                        if skill.lower() not in [s.lower() for s in candidate_skills_processed]]
        return missing_skills
    except Exception as e:
        print(f"Error finding missing skills: {e}")
        return []

def get_recommendations(candidate, internships_df, location_df):
    """Get internship recommendations for a candidate based on the system flow diagram
    
    1. Process user inputs (skills, sector, location, text)
    2. Calculate matches with available internships
    3. Score and rank internships
    4. Generate personalized recommendations with explanations
    5. Identify skill gaps and growth opportunities
    """
    recommendations = []
    
    # Step 1: Process user inputs
    # Ensure candidate dictionary has required keys
    if not isinstance(candidate, dict):
        print(f"Error: candidate must be a dictionary, got {type(candidate)}")
        candidate = {}
    
    # Set default values for missing keys
    default_candidate = {
        'skills': [],
        'sector': '',
        'location': '',
        'full_text': '',
        'education': ''
    }
    
    # Update with actual values
    for key, default_value in default_candidate.items():
        if key not in candidate or candidate[key] is None:
            candidate[key] = default_value
            
    # Step 2: Calculate matches with available internships
    for _, internship in internships_df.iterrows():
        try:
            # Calculate different match scores
            scores = {
                'skill_match': calculate_skill_match(candidate['skills'], internship['Skills_Required']),
                'sector_match': calculate_sector_match(candidate.get('sector', ''), internship['Sector']),
                'location_match': calculate_location_match(candidate.get('location', ''), internship['Location'], location_df),
                'text_similarity': calculate_text_similarity(candidate.get('full_text', ''), internship['Description'])
            }
            
            # Step 3: Score and rank internships
            # Calculate total score using weighted formula based on importance
            total_score = (scores['skill_match'] * 2.5) + \
                        (scores['sector_match'] * 2) + \
                        (scores['location_match'] * 1.5) + \
                        (scores['text_similarity'] * 1)
            
            # Step 4: Generate personalized recommendations with explanations
            reason = generate_reason(candidate, internship, scores)
            
            # Step 5: Identify skill gaps and growth opportunities
            missing_skills = find_missing_skills(candidate['skills'], internship['Skills_Required'])
        except Exception as e:
            print(f"Error processing internship {internship.get('ID', 'unknown')}: {e}")
            continue
        
        # Add to recommendations list with all calculated data
        recommendations.append({
            'internship': internship,
            'scores': scores,
            'total_score': total_score,
            'reason': reason,
            'missing_skills': missing_skills,
            'education_fit': True if candidate['education'] else False  # Simple education fit check
        })
    
    # Sort recommendations by total score
    recommendations.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Return top recommendations (max 5)
    return recommendations[:5]

def get_career_path(sector, skills, career_paths_df):
    """Get career path based on sector and skills"""
    # Handle invalid inputs
    if sector is None or pd.isna(sector) or sector == "":
        return None
    
    try:
        # Filter career paths by sector
        sector_paths = career_paths_df[career_paths_df['Sector'] == sector]
        
        if sector_paths.empty:
            return None
        
        # For now, just return the first matching path
        # In a more advanced system, we could match based on skills too
        try:
            return sector_paths.iloc[0].to_dict()
        except Exception as e:
            print(f"Error converting career path to dict: {e}")
            return None
    except Exception as e:
        print(f"Error retrieving career path for sector '{sector}': {e}")
        return None

def get_learning_resources(missing_skills, learning_resources_df):
    """Get learning resources for missing skills"""
    resources = []
    
    # Handle case where missing_skills is None or not a list
    if missing_skills is None:
        return resources
    
    if not isinstance(missing_skills, list):
        try:
            # Try to convert to list if it's something else
            missing_skills = list(missing_skills)
        except:
            print(f"Error: missing_skills is not a list and cannot be converted to a list: {missing_skills}")
            return resources
    
    try:
        for skill in missing_skills:
            if skill is None or pd.isna(skill) or skill == "":
                continue
                
            # Find resources for this skill
            try:
                skill_resources = learning_resources_df[learning_resources_df['Skill'] == skill]
                
                if not skill_resources.empty:
                    # Add up to 2 resources per skill
                    for _, resource in skill_resources.head(2).iterrows():
                        try:
                            resources.append({
                                'skill': skill,
                                'name': resource['Resource_Name'],
                                'url': resource['Resource_URL']
                            })
                        except Exception as e:
                            print(f"Error adding resource for skill {skill}: {e}")
            except Exception as e:
                print(f"Error finding resources for skill {skill}: {e}")
    except Exception as e:
        print(f"Error in get_learning_resources: {e}")
    
    return resources
