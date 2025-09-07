/**
 * Enhanced features for Smart Internship Recommender
 * Additional functionality for improved user experience
 */

// Enhanced Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Custom validation for recommendation form
    if (form.id === 'recommendation-form') {
        const skills = form.querySelectorAll('input[name="skills"]');
        const sector = form.querySelector('select[name="sector"]');
        const location = form.querySelector('select[name="location"]');
        
        if (skills.length === 0 && !sector.value && !location.value) {
            showFormError(form, 'Please provide at least one preference (skills, sector, or location)');
            isValid = false;
        }
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
    field.classList.add('error');
}

function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.classList.remove('error');
}

function showFormError(form, message) {
    let errorContainer = form.querySelector('.form-error');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'form-error alert alert-danger';
        form.insertBefore(errorContainer, form.firstChild);
    }
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
}

// Feedback System
function initializeFeedbackSystem() {
    const feedbackButtons = document.querySelectorAll('.feedback-btn');
    
    feedbackButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const internshipId = this.dataset.internshipId;
            const feedback = this.dataset.feedback;
            
            submitFeedback(internshipId, feedback);
        });
    });
}

function submitFeedback(internshipId, feedback) {
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            internship_id: internshipId,
            feedback: feedback,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Thank you for your feedback!', 'success');
        } else {
            showNotification('Error submitting feedback', 'error');
        }
    })
    .catch(error => {
        console.error('Feedback error:', error);
        showNotification('Error submitting feedback', 'error');
    });
}

// Search Features
function initializeSearchFeatures() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    if (searchInput) {
        // Add search suggestions (debounced)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                showSearchSuggestions(this.value);
            }, 300);
        });
    }
}

function handleSearch(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const searchParams = new URLSearchParams(formData);
    
    // Show loading state
    showLoadingState(true);
    
    fetch('/search', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displaySearchResults(data.results);
        showLoadingState(false);
    })
    .catch(error => {
        console.error('Search error:', error);
        showNotification('Search failed. Please try again.', 'error');
        showLoadingState(false);
    });
}

function showSearchSuggestions(query) {
    if (!query || query.length < 2) return;
    
    // Simple client-side suggestions (can be enhanced with server-side)
    const suggestions = [
        'Software Development',
        'Data Science',
        'Digital Marketing',
        'Graphic Design',
        'Content Writing',
        'Business Development',
        'Human Resources',
        'Finance',
        'Engineering',
        'Research'
    ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
    
    displaySuggestions(suggestions);
}

function displaySuggestions(suggestions) {
    let suggestionContainer = document.getElementById('search-suggestions');
    
    if (!suggestionContainer) {
        suggestionContainer = document.createElement('div');
        suggestionContainer.id = 'search-suggestions';
        suggestionContainer.className = 'search-suggestions';
        
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.parentNode.appendChild(suggestionContainer);
        }
    }
    
    suggestionContainer.innerHTML = '';
    
    if (suggestions.length > 0) {
        suggestions.slice(0, 5).forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                document.getElementById('search-input').value = suggestion;
                suggestionContainer.style.display = 'none';
            });
            suggestionContainer.appendChild(item);
        });
        suggestionContainer.style.display = 'block';
    } else {
        suggestionContainer.style.display = 'none';
    }
}

// Utility Functions
function showLoadingState(show) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => {
        el.style.display = show ? 'block' : 'none';
    });
    
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(btn => {
        btn.disabled = show;
        if (show) {
            btn.dataset.originalText = btn.textContent;
            btn.textContent = 'Processing...';
        } else {
            btn.textContent = btn.dataset.originalText || btn.textContent;
        }
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="close-btn">&times;</button>
    `;
    
    // Add to page
    let container = document.getElementById('notifications');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications';
        container.className = 'notifications-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="no-results">No internships found matching your criteria.</p>';
        return;
    }
    
    results.forEach(internship => {
        const card = createInternshipCard(internship);
        resultsContainer.appendChild(card);
    });
}

function createInternshipCard(internship) {
    const card = document.createElement('div');
    card.className = 'internship-card';
    
    card.innerHTML = `
        <div class="card-header">
            <h3>${internship.Title}</h3>
            <span class="organization">${internship.Organization || 'Not specified'}</span>
        </div>
        <div class="card-body">
            <div class="details-row">
                <span class="detail"><i class="icon-location"></i> ${internship.Location}</span>
                <span class="detail"><i class="icon-sector"></i> ${internship.Sector}</span>
                <span class="detail"><i class="icon-duration"></i> ${internship.Duration || 'Not specified'}</span>
            </div>
            <p class="description">${internship.Description?.substring(0, 150)}...</p>
        </div>
        <div class="card-footer">
            <a href="/internship/${internship.ID}" class="btn btn-primary">View Details</a>
            ${internship.Apply_URL ? `<a href="${internship.Apply_URL}" target="_blank" class="btn btn-secondary">Apply</a>` : ''}
        </div>
    `;
    
    return card;
}

// API helper functions
function makeAPIRequest(url, options = {}) {
    return fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

// Enhanced Voice Input Features
function enhanceVoiceInput() {
    const voiceBtn = document.getElementById('voice-btn');
    
    if (voiceBtn && 'webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-IN';
        
        voiceBtn.addEventListener('click', function() {
            if (this.classList.contains('recording')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
        
        recognition.onstart = function() {
            voiceBtn.classList.add('recording');
            voiceBtn.textContent = 'Listening...';
        };
        
        recognition.onresult = function(event) {
            const result = event.results[0][0].transcript;
            const voiceTextInput = document.getElementById('voice-text');
            if (voiceTextInput) {
                voiceTextInput.value = result;
                // Trigger form processing
                const form = voiceTextInput.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        };
        
        recognition.onend = function() {
            voiceBtn.classList.remove('recording');
            voiceBtn.textContent = 'Start Voice Input';
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            showNotification('Voice recognition error. Please try again.', 'error');
            voiceBtn.classList.remove('recording');
            voiceBtn.textContent = 'Start Voice Input';
        };
    }
}

// Mobile-first responsive features
function initializeMobileFeatures() {
    // Touch-friendly interactions
    const cards = document.querySelectorAll('.internship-card, .skill-chip');
    
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.classList.add('touched');
        });
        
        card.addEventListener('touchend', function() {
            setTimeout(() => {
                this.classList.remove('touched');
            }, 150);
        });
    });
    
    // Swipe gestures for navigation
    let startX, startY;
    
    document.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', function(e) {
        if (!startX || !startY) return;
        
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        // Swipe detection (horizontal swipes)
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                // Swipe left - could navigate to next page
                console.log('Swipe left detected');
            } else {
                // Swipe right - could navigate to previous page
                console.log('Swipe right detected');
            }
        }
        
        startX = null;
        startY = null;
    });
}

// Initialize all enhanced features
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeFeedbackSystem();
    initializeSearchFeatures();
    enhanceVoiceInput();
    initializeMobileFeatures();
    
    console.log('Enhanced features initialized');
});

// Export enhanced functions
window.SmartInternshipRecommender = {
    showNotification: showNotification,
    submitFeedback: submitFeedback,
    makeAPIRequest: makeAPIRequest,
    showLoadingState: showLoadingState
};
