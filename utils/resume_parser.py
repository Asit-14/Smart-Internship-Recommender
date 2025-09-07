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
    import pdfplumber
    pdfplumber_available = True
except ImportError:
    pdfplumber_available = False
    warnings.warn("pdfplumber not installed. Enhanced PDF parsing will not be available.")

try:
    import docx
except ImportError:
    docx = None
    warnings.warn("python-docx not installed. DOCX parsing will not be available.")

try:
    import docx
except ImportError:
    docx = None
    warnings.warn("python-docx not installed. DOCX parsing will not be available.")

# Temporarily disable NLTK to avoid sklearn dependency issues
try:
    # import nltk
    # from nltk.tokenize import word_tokenize
    # from nltk.corpus import stopwords
    # Download NLTK resources
    # nltk.download('punkt', quiet=True)
    # nltk.download('stopwords', quiet=True)
    nltk_available = False
    warnings.warn("NLTK temporarily disabled to avoid dependency issues.")
except ImportError:
    nltk_available = False
    warnings.warn("NLTK not installed. Advanced text processing will be limited.")

# Completely disable spaCy - don't even try to import it
spacy_available = False
nlp = None
warnings.warn("Advanced NLP features disabled. Named Entity Recognition will not be available.")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using the best available method.
    First tries pdfplumber (more reliable), then falls back to PyPDF2.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    
    # Try pdfplumber first (more reliable)
    if pdfplumber_available:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            print(f"Successfully extracted text using pdfplumber: {len(text)} characters")
            return text
        except Exception as e:
            print(f"Error with pdfplumber, falling back to PyPDF2: {e}")
    
    # Fallback to PyPDF2
    if PyPDF2 is None:
        print("No PDF parsing libraries available.")
        return text
        
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page_text = pdf_reader.pages[page_num].extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"Successfully extracted text using PyPDF2: {len(text)} characters")
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
    """Enhanced skill extraction from text using the skills database with advanced matching"""
    skills_found = []
    
    # Convert skills dataframe to a list of all skills
    all_skills = skills_df['Skill'].tolist()
    
    # Clean and prepare the text
    text_lower = text.lower()
    
    # Tokenize the text more comprehensively
    # Split by common delimiters and clean tokens
    import string
    tokens = re.split(r'[,;|\n\t\s•·▪▫◦⁃‣⁌⁍]+', text_lower)
    tokens = [token.strip(string.punctuation + ' ') for token in tokens if token.strip()]
    
    # Create different text representations for better matching
    text_no_punctuation = re.sub(r'[^\w\s]', ' ', text_lower)
    text_cleaned = ' '.join(text_no_punctuation.split())
    
    # Check for each skill in the text using multiple methods
    for skill in all_skills:
        skill_lower = skill.lower().strip()
        if not skill_lower:
            continue
            
        try:
            skill_found = False
            
            # Method 1: Exact word boundary matching
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_cleaned):
                skill_found = True
            
            # Method 2: Check for skill variations (remove common connectors)
            skill_words = skill_lower.replace('-', ' ').replace('_', ' ').split()
            if len(skill_words) > 1:
                # Check if all words of multi-word skill are present
                if all(word in text_cleaned for word in skill_words):
                    skill_found = True
            
            # Method 3: Check in individual tokens for partial matches
            for token in tokens:
                if skill_lower == token or (len(skill_lower) > 3 and skill_lower in token):
                    skill_found = True
                    break
            
            # Method 4: Handle common programming languages and frameworks
            skill_patterns = {
                'javascript': ['js', 'javascript', 'node.js', 'nodejs'],
                'c++': ['c++', 'cpp', 'c plus plus'],
                'c#': ['c#', 'csharp', 'c sharp'],
                'python': ['python', 'py'],
                'java': ['java', 'openjdk'],
                'react': ['react', 'reactjs', 'react.js'],
                'angular': ['angular', 'angularjs'],
                'vue': ['vue', 'vuejs', 'vue.js'],
                'sql': ['sql', 'mysql', 'postgresql', 'sqlite']
            }
            
            if skill_lower in skill_patterns:
                for pattern in skill_patterns[skill_lower]:
                    if re.search(r'\b' + re.escape(pattern) + r'\b', text_cleaned):
                        skill_found = True
                        break
            
            # Method 5: Common skill abbreviations and acronyms
            skill_abbreviations = {
                'machine learning': ['ml', 'machine learning'],
                'artificial intelligence': ['ai', 'artificial intelligence'],
                'user interface': ['ui', 'user interface'],
                'user experience': ['ux', 'user experience'],
                'application programming interface': ['api', 'apis'],
                'hyper text markup language': ['html', 'html5'],
                'cascading style sheets': ['css', 'css3'],
                'structured query language': ['sql'],
                'representational state transfer': ['rest', 'restful']
            }
            
            if skill_lower in skill_abbreviations:
                for abbrev in skill_abbreviations[skill_lower]:
                    if re.search(r'\b' + re.escape(abbrev) + r'\b', text_cleaned):
                        skill_found = True
                        break
            
            if skill_found and skill not in skills_found:
                skills_found.append(skill)
                
        except Exception as e:
            print(f"Error processing skill '{skill}': {e}")
            continue
    
    # Remove duplicates while preserving order
    unique_skills = []
    for skill in skills_found:
        if skill not in unique_skills:
            unique_skills.append(skill)
    
    return unique_skills

def extract_education(text, education_df):
    """Enhanced education information extraction from text"""
    education_found = []
    all_education = education_df['Category'].tolist()
    
    # Clean text for better matching
    text_lower = text.lower()
    
    # Common education keywords and patterns
    education_patterns = {
        'bachelor': ['bachelor', 'b.tech', 'btech', 'b.e', 'be', 'b.sc', 'bsc', 'ba', 'b.a', 'bs', 'b.s'],
        'master': ['master', 'm.tech', 'mtech', 'm.e', 'me', 'm.sc', 'msc', 'ma', 'm.a', 'ms', 'm.s', 'mba'],
        'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
        'diploma': ['diploma', 'certificate'],
        'high school': ['high school', '12th', 'xii', 'higher secondary', 'intermediate'],
        '10th': ['10th', 'matriculation', 'secondary']
    }
    
    # Check for each education category
    for edu in all_education:
        edu_lower = edu.lower()
        # Direct matching
        if re.search(r'\b' + re.escape(edu_lower) + r'\b', text_lower):
            education_found.append(edu)
            continue
            
        # Pattern matching for common variations
        for pattern_key, patterns in education_patterns.items():
            if pattern_key in edu_lower:
                for pattern in patterns:
                    if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
                        education_found.append(edu)
                        break
    
    # Additional pattern matching for degrees not in the database
    degree_patterns = [
        r'\b(bachelor|b\.?tech|b\.?e|b\.?sc|b\.?a|bs|b\.?s)\b',
        r'\b(master|m\.?tech|m\.?e|m\.?sc|m\.?a|ms|m\.?s|mba)\b',
        r'\b(phd|ph\.?d|doctorate|doctoral)\b',
        r'\b(diploma|certificate)\b'
    ]
    
    for pattern in degree_patterns:
        if re.search(pattern, text_lower):
            # Map to general categories if not already found
            if pattern == degree_patterns[0] and 'Bachelor' not in education_found:
                education_found.append('Bachelor')
            elif pattern == degree_patterns[1] and 'Master' not in education_found:
                education_found.append('Master')
            elif pattern == degree_patterns[2] and 'PhD' not in education_found:
                education_found.append('PhD')
            elif pattern == degree_patterns[3] and 'Diploma' not in education_found:
                education_found.append('Diploma')
    
    return list(set(education_found))

def extract_location(text, locations_df):
    """Enhanced location information extraction from text"""
    locations_found = []
    
    # Extract all cities and states from the locations dataframe
    cities = locations_df['City'].dropna().tolist()
    states = locations_df['State'].dropna().unique().tolist()
    
    text_lower = text.lower()
    
    # Check for cities in the text
    for city in cities:
        city_lower = city.lower()
        if re.search(r'\b' + re.escape(city_lower) + r'\b', text_lower):
            locations_found.append(city)
    
    # Check for states in the text
    for state in states:
        state_lower = state.lower()
        if re.search(r'\b' + re.escape(state_lower) + r'\b', text_lower):
            locations_found.append(state)
    
    # Common location patterns and keywords
    location_keywords = ['address', 'location', 'based in', 'from', 'lives in', 'residing in']
    
    # Look for address patterns
    address_patterns = [
        r'(\w+(?:\s+\w+)*),\s*(\w+(?:\s+\w+)*)',  # City, State pattern
        r'(\w+(?:\s+\w+)*)\s*,\s*(\w+)',           # Simpler city, state
    ]
    
    for pattern in address_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            potential_city = match.group(1).strip()
            potential_state = match.group(2).strip()
            
            # Check if these match our known cities/states
            if potential_city.lower() in [c.lower() for c in cities]:
                locations_found.append(potential_city.title())
            if potential_state.lower() in [s.lower() for s in states]:
                locations_found.append(potential_state.title())
    
    # Remove duplicates while preserving order
    unique_locations = []
    for location in locations_found:
        if location not in unique_locations:
            unique_locations.append(location)
    
    return unique_locations

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
