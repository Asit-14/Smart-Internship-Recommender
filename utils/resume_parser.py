import pandas as pd
import re
import os
import warnings

# Handle potential missing dependencies gracefully
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
    warnings.warn("PyPDF2 not installed. PDF parsing will not be available.")

try:
    import docx
except ImportError:
    docx = None
    warnings.warn("python-docx not installed. DOCX parsing will not be available.")

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    # Download NLTK resources
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk_available = True
except ImportError:
    nltk_available = False
    warnings.warn("NLTK not installed. Advanced text processing will be limited.")

# Completely disable spaCy - don't even try to import it
spacy_available = False
nlp = None
warnings.warn("Advanced NLP features disabled. Named Entity Recognition will not be available.")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    text = ""
    if PyPDF2 is None:
        print("PyPDF2 is not installed. Cannot extract text from PDF.")
        return text
        
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file"""
    text = ""
    if docx is None:
        print("python-docx is not installed. Cannot extract text from DOCX.")
        return text
        
    try:
        doc = docx.Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
    return text

def extract_text_from_resume(file_path):
    """Extract text from resume based on file extension"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_skills(text, skills_df):
    """Extract skills from text using the skills database"""
    skills_found = []
    # Convert skills dataframe to a list of all skills
    all_skills = skills_df['Skill'].tolist()
    
    # Clean and tokenize the text
    text = text.lower()
    
    # Use NLTK for tokenization if available, otherwise fallback to simple split
    if nltk_available:
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fallback if tokenization fails
            tokens = text.split()
    else:
        tokens = text.split()
    
    # Check for each skill in the text
    for skill in all_skills:
        skill_lower = skill.lower()
        try:
            # Check for exact matches (accounting for word boundaries)
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
                skills_found.append(skill)
            # Also check in tokens for multi-word skills
            elif len(skill_lower.split()) > 1:
                if all(word in tokens for word in skill_lower.split()):
                    skills_found.append(skill)
        except Exception as e:
            print(f"Error matching skill {skill}: {e}")
            continue
    
    return list(set(skills_found))

def extract_education(text, education_df):
    """Extract education information from text"""
    education_found = []
    all_education = education_df['Category'].tolist()
    
    for edu in all_education:
        if re.search(r'\b' + re.escape(edu.lower()) + r'\b', text.lower()):
            education_found.append(edu)
    
    return list(set(education_found))

def extract_location(text, locations_df):
    """Extract location information from text"""
    locations_found = []
    
    # Extract all cities and states from the locations dataframe
    cities = locations_df['City'].tolist()
    states = locations_df['State'].tolist()
    
    # Check for cities and states in the text
    for city in cities:
        if re.search(r'\b' + re.escape(city.lower()) + r'\b', text.lower()):
            locations_found.append(city)
    
    for state in states:
        if re.search(r'\b' + re.escape(state.lower()) + r'\b', text.lower()):
            locations_found.append(state)
    
    return list(set(locations_found))

def parse_resume(file_path, skills_df, education_df, locations_df):
    """Parse a resume and extract relevant information"""
    try:
        # Extract text from resume
        text = extract_text_from_resume(file_path)
        
        if not text:
            print("Warning: No text extracted from resume")
            return {
                'skills': [],
                'education': [],
                'locations': [],
                'full_text': ""
            }
        
        # Extract skills, education, and location
        try:
            skills = extract_skills(text, skills_df)
        except Exception as e:
            print(f"Error extracting skills: {e}")
            skills = []
            
        try:
            education = extract_education(text, education_df)
        except Exception as e:
            print(f"Error extracting education: {e}")
            education = []
            
        try:
            locations = extract_location(text, locations_df)
        except Exception as e:
            print(f"Error extracting locations: {e}")
            locations = []
        
        return {
            'skills': skills,
            'education': education,
            'locations': locations,
            'full_text': text
        }
        
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {
            'skills': [],
            'education': [],
            'locations': [],
            'full_text': ""
        }
