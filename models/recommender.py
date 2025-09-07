import pandas as pd
import numpy as np
# Temporarily commenting out sklearn imports for basic functionality
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
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
    """Enhanced skill match calculation with fuzzy matching and skill similarity"""
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
        candidate_skills_processed = [skill.lower().strip() for skill in preprocess_skills(candidate_skills) if skill]
        internship_skills_processed = [skill.lower().strip() for skill in preprocess_skills(internship_skills) if skill]
        
        # Check if we have any processed skills
        if not candidate_skills_processed or not internship_skills_processed:
            return 0
        
        # Method 1: Direct exact matches
        common_skills = set(candidate_skills_processed).intersection(set(internship_skills_processed))
        exact_match_score = len(common_skills) / len(internship_skills_processed)
        
        # Method 2: Fuzzy matching for similar skills
        fuzzy_matches = 0
        skill_similarity_map = {
            # Programming languages
            'python': ['py', 'python3', 'python2'],
            'javascript': ['js', 'node.js', 'nodejs', 'ecmascript'],
            'java': ['openjdk', 'oracle java'],
            'c++': ['cpp', 'c plus plus'],
            'c#': ['csharp', 'c sharp', 'dotnet'],
            
            # Web technologies
            'html': ['html5', 'hyper text markup language'],
            'css': ['css3', 'cascading style sheets'],
            'react': ['reactjs', 'react.js'],
            'angular': ['angularjs'],
            'vue': ['vuejs', 'vue.js'],
            
            # Databases
            'sql': ['mysql', 'postgresql', 'sqlite', 'mssql'],
            'mongodb': ['mongo', 'nosql'],
            
            # Tools and frameworks
            'git': ['github', 'gitlab', 'version control'],
            'docker': ['containerization'],
            'kubernetes': ['k8s', 'orchestration'],
            
            # Data science
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'data analysis': ['data analytics', 'data science'],
            'tensorflow': ['tf'],
            'pytorch': ['torch'],
            
            # Design
            'photoshop': ['adobe photoshop', 'ps'],
            'illustrator': ['adobe illustrator', 'ai'],
            'figma': ['ui design', 'ux design'],
        }
        
        for internship_skill in internship_skills_processed:
            if internship_skill in common_skills:
                continue  # Already counted in exact matches
                
            for candidate_skill in candidate_skills_processed:
                if candidate_skill in common_skills:
                    continue  # Already counted
                
                # Check similarity mappings
                skill_matched = False
                for base_skill, variations in skill_similarity_map.items():
                    if (base_skill == internship_skill or internship_skill in variations) and \
                       (base_skill == candidate_skill or candidate_skill in variations):
                        fuzzy_matches += 1
                        skill_matched = True
                        break
                
                if skill_matched:
                    break
                
                # Simple substring matching for longer skills
                if len(internship_skill) > 4 and len(candidate_skill) > 4:
                    if internship_skill in candidate_skill or candidate_skill in internship_skill:
                        fuzzy_matches += 0.5  # Partial credit for substring matches
        
        # Method 3: Calculate weighted score
        fuzzy_match_score = min(fuzzy_matches / len(internship_skills_processed), 1.0)
        
        # Combined score with weights
        total_score = (exact_match_score * 0.8) + (fuzzy_match_score * 0.2)
        
        return min(total_score, 1.0)  # Cap at 1.0
        
    except Exception as e:
        print(f"Error in enhanced skill matching: {e}")
        return 0

def normalize_sector(user_sector):
    """Normalize user input sector to match dataset sectors"""
    if not user_sector or pd.isna(user_sector):
        return ""
    
    user_lower = user_sector.lower().strip()
    
    # Mapping user input to actual sectors in dataset
    sector_normalizations = {
        'pharmacy': 'Healthcare',
        'pharmaceutical': 'Healthcare', 
        'medical': 'Healthcare',
        'health': 'Healthcare',
        'healthcare': 'Healthcare',
        'hospital': 'Healthcare',
        'medicine': 'Healthcare',
        'pharma': 'Healthcare',
        
        'it': 'IT',
        'software': 'IT',
        'technology': 'IT',
        'computer': 'IT',
        'programming': 'IT',
        'tech': 'IT',
        'information technology': 'IT',
        
        'business': 'Business',
        'marketing': 'Business',
        'sales': 'Business',
        'management': 'Business',
        'commerce': 'Business',
        'mba': 'Business',
        
        'finance': 'Finance',
        'banking': 'Finance',
        'financial': 'Finance',
        'accounting': 'Finance',
        'investment': 'Finance',
        
        'engineering': 'Engineering',
        'mechanical': 'Engineering',
        'civil': 'Engineering',
        'electrical': 'Engineering',
        'chemical': 'Engineering',
        'automotive': 'Engineering',
        
        'education': 'Education',
        'teaching': 'Education',
        'academic': 'Education',
        'training': 'Education',
        'learning': 'Education',
        
        'design': 'Creative',
        'creative': 'Creative',
        'art': 'Creative',
        'graphic': 'Creative',
        'ui': 'Creative',
        'ux': 'Creative',
        
        'social': 'Social Work',
        'ngo': 'Social Work',
        'community': 'Social Work',
        'social work': 'Social Work',
        
        'media': 'Media',
        'journalism': 'Media',
        'communication': 'Media',
        'content': 'Media'
    }
    
    # Direct match
    if user_lower in sector_normalizations:
        return sector_normalizations[user_lower]
    
    # Partial match
    for key, value in sector_normalizations.items():
        if key in user_lower or user_lower in key:
            return value
    
    # Return original if no mapping found
    return user_sector.title()

def calculate_sector_match(candidate_sector, internship_sector):
    """Enhanced sector match between candidate and internship with fuzzy matching"""
    if pd.isna(candidate_sector) or pd.isna(internship_sector):
        return 0
    
    candidate_lower = candidate_sector.lower().strip()
    internship_lower = internship_sector.lower().strip()
    
    # Exact match
    if candidate_lower == internship_lower:
        return 1
    
    # Handle common sector variations and related fields
    sector_mappings = {
        'pharmacy': ['healthcare', 'pharmaceutical', 'medical', 'health'],
        'healthcare': ['pharmacy', 'pharmaceutical', 'medical', 'health', 'hospital'],
        'pharmaceutical': ['pharmacy', 'healthcare', 'medical', 'health'],
        'medical': ['healthcare', 'pharmacy', 'pharmaceutical', 'health'],
        'it': ['information technology', 'software', 'technology', 'computer science', 'tech'],
        'software': ['it', 'information technology', 'technology', 'computer science', 'tech'],
        'technology': ['it', 'software', 'information technology', 'tech'],
        'business': ['marketing', 'management', 'finance', 'sales', 'commerce'],
        'marketing': ['business', 'digital marketing', 'advertising', 'sales'],
        'finance': ['business', 'banking', 'accounting', 'financial'],
        'engineering': ['mechanical', 'civil', 'electrical', 'chemical', 'automotive'],
        'education': ['teaching', 'academic', 'training', 'learning'],
        'design': ['graphic design', 'ui/ux', 'creative', 'art']
    }
    
    # Check if candidate sector maps to internship sector
    if candidate_lower in sector_mappings:
        for related_sector in sector_mappings[candidate_lower]:
            if related_sector in internship_lower:
                return 0.8  # High but not perfect match for related sectors
    
    # Check if internship sector maps to candidate sector
    if internship_lower in sector_mappings:
        for related_sector in sector_mappings[internship_lower]:
            if related_sector in candidate_lower:
                return 0.8
    
    # Partial string matching for longer sector names
    if len(candidate_lower) > 3 and len(internship_lower) > 3:
        if candidate_lower in internship_lower or internship_lower in candidate_lower:
            return 0.6
    
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
    """Enhanced text similarity between resume and internship description"""
    if pd.isna(candidate_text) or pd.isna(internship_description):
        return 0
    
    # Convert to string if not already
    candidate_text = str(candidate_text).lower()
    internship_description = str(internship_description).lower()
    
    if not candidate_text.strip() or not internship_description.strip():
        return 0
    
    try:
        # Method 1: Common word similarity (basic)
        candidate_words = set(re.findall(r'\b\w+\b', candidate_text))
        internship_words = set(re.findall(r'\b\w+\b', internship_description))
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        candidate_words = candidate_words - stop_words
        internship_words = internship_words - stop_words
        
        if not candidate_words or not internship_words:
            return 0
        
        # Basic Jaccard similarity
        common_words = candidate_words.intersection(internship_words)
        union_words = candidate_words.union(internship_words)
        basic_similarity = len(common_words) / len(union_words) if union_words else 0
        
        # Method 2: Keyword importance weighting
        # Important keywords that should have higher weight
        important_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'machine learning', 'data science', 'artificial intelligence',
            'web development', 'mobile development', 'software engineering',
            'database', 'sql', 'mongodb', 'postgresql',
            'cloud', 'aws', 'azure', 'gcp',
            'devops', 'docker', 'kubernetes',
            'frontend', 'backend', 'fullstack',
            'api', 'rest', 'graphql',
            'testing', 'automation', 'ci/cd',
            'agile', 'scrum', 'project management'
        }
        
        # Count important keyword matches
        important_matches = 0
        total_important_in_internship = 0
        
        for keyword in important_keywords:
            if keyword in internship_description:
                total_important_in_internship += 1
                if keyword in candidate_text:
                    important_matches += 1
        
        keyword_similarity = important_matches / total_important_in_internship if total_important_in_internship > 0 else 0
        
        # Method 3: N-gram similarity for phrases
        def get_bigrams(text):
            words = re.findall(r'\b\w+\b', text)
            return set(zip(words[:-1], words[1:]))
        
        candidate_bigrams = get_bigrams(candidate_text)
        internship_bigrams = get_bigrams(internship_description)
        
        if candidate_bigrams and internship_bigrams:
            common_bigrams = candidate_bigrams.intersection(internship_bigrams)
            bigram_similarity = len(common_bigrams) / len(candidate_bigrams.union(internship_bigrams))
        else:
            bigram_similarity = 0
        
        # Weighted combination of similarities
        final_similarity = (basic_similarity * 0.4) + (keyword_similarity * 0.4) + (bigram_similarity * 0.2)
        
        return min(final_similarity, 1.0)  # Cap at 1.0
        
    except Exception as e:
        print(f"Error calculating enhanced text similarity: {e}")
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
    
    # Update with actual values and normalize sector
    for key, default_value in default_candidate.items():
        if key not in candidate or candidate[key] is None:
            candidate[key] = default_value
    
    # Normalize the sector to match dataset values
    if candidate['sector']:
        original_sector = candidate['sector']
        candidate['sector'] = normalize_sector(candidate['sector'])
        print(f"Normalized sector '{original_sector}' to '{candidate['sector']}'")
            
    # Step 2: Calculate matches with available internships
    # Pre-filter internships by sector if specified
    filtered_internships = internships_df
    if candidate.get('sector') and candidate['sector'].strip():
        print(f"Filtering internships by sector: {candidate['sector']}")
        # Filter for exact sector matches and related sectors
        sector_matches = []
        for _, internship in internships_df.iterrows():
            # For strict filtering, we want high sector match
            if internship['Sector'] == candidate['sector']:
                sector_matches.append(internship)
        
        if sector_matches:
            filtered_internships = pd.DataFrame(sector_matches)
            print(f"Found {len(filtered_internships)} internships exactly matching sector '{candidate['sector']}'")
        else:
            # If no exact matches, try related sectors
            for _, internship in internships_df.iterrows():
                sector_score = calculate_sector_match(candidate['sector'], internship['Sector'])
                if sector_score >= 0.8:  # High threshold for related sectors
                    sector_matches.append(internship)
            
            if sector_matches:
                filtered_internships = pd.DataFrame(sector_matches)
                print(f"Found {len(filtered_internships)} internships with related sectors to '{candidate['sector']}'")
            else:
                print(f"No internships found for sector '{candidate['sector']}', showing all internships")
                filtered_internships = internships_df
    
    for _, internship in filtered_internships.iterrows():
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

# Temporarily disabled TF-IDF functionality for basic app startup
def recommend_jobs_tfidf(user_profile, internships, top_n=5):
    """
    Advanced TF-IDF based recommendation system - TEMPORARILY DISABLED
    """
    print("TF-IDF functionality temporarily disabled")
    return []

def hybrid_recommendation(user_profile, internships_df, locations_df=None, top_n=5, use_tfidf=False):
    """
    Hybrid recommendation system - using rule-based only for now
    """
    # Fallback to rule-based recommendations only
    return get_recommendations(user_profile, internships_df, locations_df, top_n=top_n)
    """
    Advanced TF-IDF based recommendation system.
    
    Args:
        user_profile (dict): User profile with skills, education, etc.
        internships (list): List of internship dictionaries
        top_n (int): Number of top recommendations to return
        
    Returns:
        list: Ranked internships with similarity scores
    """
    try:
        if not internships:
            print("No internships provided for TF-IDF recommendation")
            return []
        
        # Prepare user profile text
        user_skills = user_profile.get('skills', [])
        user_education = user_profile.get('education', '')
        user_sector = user_profile.get('sector', '')
        user_location = user_profile.get('location', '')
        user_text = user_profile.get('full_text', '')
        
        # Create user profile text
        if isinstance(user_skills, list):
            skills_text = ' '.join(user_skills)
        else:
            skills_text = str(user_skills)
            
        user_profile_text = f"{skills_text} {user_education} {user_sector} {user_location} {user_text}".strip()
        
        # Create internship descriptions
        internship_texts = []
        for internship in internships:
            description = internship.get('Description', '')
            skills_required = internship.get('Skills_Required', '')
            title = internship.get('Title', '')
            sector = internship.get('Sector', '')
            education_req = internship.get('Education_Required', '')
            
            # Combine all relevant text fields
            internship_text = f"{title} {description} {skills_required} {sector} {education_req}".strip()
            internship_texts.append(internship_text)
        
        # Prepare documents for TF-IDF
        documents = [user_profile_text] + internship_texts
        
        # Remove empty documents
        if not any(doc.strip() for doc in documents):
            print("No valid text content for TF-IDF analysis")
            return []
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            min_df=1,  # Minimum document frequency
            lowercase=True
        )
        
        # Fit and transform documents
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
        except ValueError as e:
            print(f"TF-IDF vectorization error: {e}")
            return []
        
        # Calculate cosine similarity between user profile and internships
        user_vector = tfidf_matrix[0:1]  # First document is user profile
        internship_vectors = tfidf_matrix[1:]  # Rest are internships
        
        similarities = cosine_similarity(user_vector, internship_vectors).flatten()
        
        # Create ranked results
        ranked_internships = []
        for i, similarity in enumerate(similarities):
            if i < len(internships):  # Safety check
                ranked_internships.append({
                    'internship': internships[i],
                    'similarity_score': float(similarity),
                    'rank': i + 1
                })
        
        # Sort by similarity score in descending order
        ranked_internships.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return top N recommendations
        top_recommendations = ranked_internships[:top_n]
        
        print(f"TF-IDF recommendation completed. Top similarity scores: {[r['similarity_score'] for r in top_recommendations[:3]]}")
        
        return top_recommendations
        
    except Exception as e:
        print(f"Error in TF-IDF recommendation: {e}")
        return []

def hybrid_recommendation(user_profile, internships_df, locations_df=None, top_n=5, use_tfidf=True):
    """
    Hybrid recommendation system combining rule-based and TF-IDF approaches.
    
    Args:
        user_profile (dict): User profile
        internships_df (DataFrame): Internships dataframe
        locations_df (DataFrame): Locations dataframe
        top_n (int): Number of recommendations
        use_tfidf (bool): Whether to use TF-IDF for enhanced scoring
        
    Returns:
        list: Hybrid recommendations with combined scores
    """
    try:
        # Get traditional rule-based recommendations
        rule_based_recs = get_recommendations(user_profile, internships_df, locations_df, top_n=top_n*2)
        
        if not rule_based_recs:
            return []
        
        # If TF-IDF is disabled or fails, return rule-based results
        if not use_tfidf:
            return rule_based_recs[:top_n]
        
        # Convert to list of dictionaries for TF-IDF
        internships_list = [rec['internship'] for rec in rule_based_recs]
        
        # Get TF-IDF recommendations
        tfidf_recs = recommend_jobs_tfidf(user_profile, internships_list, top_n=len(internships_list))
        
        if not tfidf_recs:
            print("TF-IDF failed, using rule-based recommendations")
            return rule_based_recs[:top_n]
        
        # Combine scores (weighted average)
        combined_recs = []
        for rule_rec in rule_based_recs:
            # Find corresponding TF-IDF recommendation
            internship_id = rule_rec['internship'].get('ID', '')
            tfidf_score = 0
            
            for tfidf_rec in tfidf_recs:
                if tfidf_rec['internship'].get('ID', '') == internship_id:
                    tfidf_score = tfidf_rec['similarity_score']
                    break
            
            # Combine scores (70% rule-based, 30% TF-IDF)
            combined_score = (0.7 * rule_rec['score']) + (0.3 * tfidf_score)
            
            combined_rec = {
                'internship': rule_rec['internship'],
                'score': combined_score,
                'rule_score': rule_rec['score'],
                'tfidf_score': tfidf_score,
                'reason': rule_rec['reason'],
                'missing_skills': rule_rec.get('missing_skills', [])
            }
            combined_recs.append(combined_rec)
        
        # Sort by combined score
        combined_recs.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"Hybrid recommendation completed with {len(combined_recs)} results")
        return combined_recs[:top_n]
        
    except Exception as e:
        print(f"Error in hybrid recommendation: {e}")
        # Fallback to rule-based recommendations
        return get_recommendations(user_profile, internships_df, locations_df, top_n=top_n)
