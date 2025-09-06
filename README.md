# Smart Internship Recommender

A government-style AI-powered internship recommendation system that helps users find personalized internships based on their skills, education, and interests.

## Features

- **Personalized Recommendations**: Get top 3-5 internship recommendations based on your profile
- **Resume Analysis**: Upload your resume for automatic skill extraction
- **Explainable AI**: Each recommendation comes with a reason why it matches your profile
- **Skill Gap Analysis**: Identify skills you need to develop and access learning resources
- **Career Path Visualization**: See the potential career path for each recommended internship
- **Government-Style UI**: Clean, accessible interface with national emblem and official look
- **Voice Input Support**: Speak your preferences for a hands-free experience
- **Language Toggle**: Switch between English and Hindi (planned feature)
- **Mobile-First Design**: Touch-friendly UI with minimal text and large targets
- **Rural Optimization**: Works in low-bandwidth and low-resource environments

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy
- **NLP & ML**: scikit-learn, NLTK, spaCy
- **Document Processing**: PyPDF2, python-docx

## Directory Structure

```
Smart-Internship-Recommender/
├── app/                       # Flask application
│   ├── static/                # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/             # HTML templates
│   ├── __init__.py            # Flask app initialization
│   └── routes.py              # Application routes
├── data/                      # Dataset files
│   ├── internships.csv        # Internship listings
│   ├── skills.csv             # Skills knowledge base
│   ├── locations.csv          # Location mapping
│   ├── education.csv          # Education categories
│   ├── sectors.csv            # Industry sectors
│   ├── career_paths.csv       # Career progression paths
│   └── learning_resources.csv # Skill development resources
├── models/                    # AI models
│   └── recommender.py         # Recommendation engine
├── services/                  # Business logic
│   └── internship_service.py  # Service layer for internships
├── utils/                     # Utility functions
│   └── resume_parser.py       # Resume parsing functionality
├── requirements.txt           # Python dependencies
└── run.py                     # Application entry point
│   ├── nginx.conf          # Nginx configuration for production
│   └── README.md           # React frontend documentation
│
├── data/
│   └── internships.csv     # Sample internship dataset
│
├── jobs_cleaned.csv        # Large dataset (1.6+ million entries)
```

## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/Asit-14/Smart-Internship-Recommender.git
cd Smart-Internship-Recommender
```

2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install spaCy language model
```bash
python -m spacy download en_core_web_sm
```

5. Run the application
```bash
python run.py
```

6. Open your browser and go to `http://127.0.0.1:5000/`

## Usage Flow

1. **Input**: Choose between form input, resume upload, or voice input
2. **Processing**: The system matches your profile with available internships
3. **Results**: View personalized recommendations with match explanations
4. **Details**: Explore skill gaps, learning resources, and career paths for each recommendation
5. **Apply**: Click "Apply Now" to visit the internship application page
6. **Feedback**: Rate the recommendations to help improve the system

## Implementation Details

### Resume Parser

The resume parser uses NLP techniques to extract:
- Skills by matching against a knowledge base of ~200 skills
- Education information
- Location preferences
- Full-text content for semantic matching

### Recommendation Engine

Uses a hybrid approach combining:
- Skill matching (weighted 2x)
- Sector matching (weighted 2x)
- Location matching (weighted 1x)
- Text similarity using TF-IDF (weighted 3x)

### Skill Gap Analysis

For each recommendation:
- Identifies skills required by the internship but missing from the candidate's profile
- Provides links to relevant learning resources (SWAYAM, Coursera)
- Helps candidates prepare for the internship role

### Career Path Suggestion

Shows a potential career progression:
- Starting with the internship position
- Followed by entry-level role
- Mid-level position
- Senior-level position

## Deployment Options

### Local Deployment
- Run directly using Flask's development server
- Suitable for demonstration and testing

### Cloud Deployment
- Deploy to Heroku, Render, or Railway
- Use simple web service configuration

### Government Server Deployment
- Move to secure government infrastructure
- Implement HTTPS and database integration

## Future Enhancements

1. **Database Integration**: Move from CSV to a proper database
2. **Admin Dashboard**: Add analytics for government officials
3. **Enhanced NLP**: Improve resume parsing accuracy
4. **Full Language Support**: Complete Hindi translations
5. **WhatsApp Integration**: Text-based recommendations for non-smartphone users
6. **Voice Interface**: Improve spoken instructions for low-literacy users

## License

This project is licensed under the MIT License - see the LICENSE file for details.
