// Enhanced Smart Internship Recommender JavaScript

// Global variables
let translations = {};
let currentLanguage = 'en';
let availableLanguages = [
    { code: 'en', name: 'English', nativeName: 'English', rtl: false },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', rtl: false },
    { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া', rtl: false },
    { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', rtl: false },
    { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', rtl: false },
    { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', rtl: false },
    { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', rtl: false },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी', rtl: false },
    { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', rtl: false },
    { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', rtl: false },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', rtl: false },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', rtl: false },
    { code: 'ur', name: 'Urdu', nativeName: 'اردو', rtl: true }
];
let skillsData = {};

// Initialize the app
function initializeApp() {
    console.log('Initializing Smart Internship Recommender...');
    
    // Initialize components
    initializeSkillsSelector();
    initializeFormValidation();
    initializeFeedbackSystem();
    initializeSearchFeatures();
    
    // Initialize language system
    initializeLanguage();
    initializeLanguageDropdown();
    
    console.log('Smart Internship Recommender initialized successfully');
}

// Language Functions
function initializeLanguage() {
    console.log('Starting language initialization...');
    
    // Get stored language preference
    currentLanguage = localStorage.getItem('preferredLanguage') || 'en';
    console.log('Current language:', currentLanguage);
    
    // Set HTML attributes
    document.documentElement.lang = currentLanguage;
    
    // Load translations and update UI
    loadAndApplyTranslations(currentLanguage);
    updateLanguageDropdownDisplay();
}

function initializeLanguageDropdown() {
    console.log('Setting up language dropdown...');
    
    const dropdownBtn = document.getElementById('language-dropdown-btn');
    const dropdown = document.getElementById('language-dropdown');
    
    if (!dropdownBtn || !dropdown) {
        console.warn('Language dropdown elements not found');
        return;
    }
    
    // Populate dropdown
    populateLanguageDropdown();
    
    // Add click handler for dropdown button
    dropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.toggle('show');
        console.log('Dropdown toggled');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdownBtn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
    
    console.log('Language dropdown initialized');
}

function populateLanguageDropdown() {
    const dropdown = document.getElementById('language-dropdown');
    if (!dropdown) return;
    
    dropdown.innerHTML = '';
    
    availableLanguages.forEach(lang => {
        const option = document.createElement('div');
        option.className = 'dropdown-item';
        option.textContent = `${lang.nativeName} (${lang.name})`;
        option.dataset.langCode = lang.code;
        
        if (lang.code === currentLanguage) {
            option.classList.add('active');
        }
        
        option.addEventListener('click', function(e) {
            e.preventDefault();
            switchToLanguage(lang.code);
            dropdown.classList.remove('show');
        });
        
        dropdown.appendChild(option);
    });
    
    console.log('Language dropdown populated with', availableLanguages.length, 'options');
}

function switchToLanguage(langCode) {
    console.log('Switching to language:', langCode);
    
    currentLanguage = langCode;
    localStorage.setItem('preferredLanguage', langCode);
    
    // Handle RTL languages
    const langConfig = availableLanguages.find(lang => lang.code === langCode);
    if (langConfig && langConfig.rtl) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
    } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
    }
    
    document.documentElement.lang = langCode;
    
    // Update UI
    updateLanguageDropdownDisplay();
    loadAndApplyTranslations(langCode);
    
    console.log('Language switched to:', langCode);
}

function updateLanguageDropdownDisplay() {
    const currentLangText = document.getElementById('current-lang-text');
    if (!currentLangText) return;
    
    const currentLang = availableLanguages.find(lang => lang.code === currentLanguage);
    if (currentLang) {
        currentLangText.textContent = currentLang.nativeName;
    }
    
    // Update active state in dropdown
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.classList.remove('active');
        if (item.dataset.langCode === currentLanguage) {
            item.classList.add('active');
        }
    });
}

function loadAndApplyTranslations(lang) {
    console.log('Loading translations for:', lang);
    
    fetch(`/static/locales/${lang}.json?t=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${lang}`);
            }
            return response.json();
        })
        .then(data => {
            translations = data;
            console.log('Translations loaded successfully');
            applyTranslations();
        })
        .catch(error => {
            console.error('Error loading translations:', error);
        });
}

function applyTranslations() {
    if (!translations || Object.keys(translations).length === 0) {
        console.warn('No translations available');
        return;
    }
    
    const elements = document.querySelectorAll('[data-i18n]');
    console.log('Applying translations to', elements.length, 'elements');
    
    elements.forEach(element => {
        try {
            const key = element.getAttribute('data-i18n');
            const parts = key.split('.');
            
            let value = translations;
            for (const part of parts) {
                if (!value || !value[part]) {
                    console.warn('Translation key not found:', key);
                    return;
                }
                value = value[part];
            }
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.hasAttribute('placeholder')) {
                    element.setAttribute('placeholder', value);
                } else {
                    element.value = value;
                }
            } else {
                element.innerHTML = value;
            }
        } catch (error) {
            console.error('Error applying translation to element:', element, error);
        }
    });
}

// Skills Selector
function initializeSkillsSelector() {
    const skillsContainer = document.getElementById('skills-container');
    if (!skillsContainer) return;
    
    const input = document.getElementById('skills-input');
    const dropdown = document.getElementById('skills-dropdown');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    const selectedSkills = new Set();
    
    // Get skills from page data
    let allSkills = [];
    const skillsData = document.getElementById('skills-data');
    if (skillsData) {
        try {
            allSkills = JSON.parse(skillsData.textContent);
        } catch (e) {
            console.error('Error parsing skills data:', e);
            allSkills = ['Python', 'Java', 'JavaScript', 'Communication', 'Leadership'];
        }
    }
    
    // Create hidden inputs for selected skills
    function updateHiddenInputs() {
        const existingInputs = document.querySelectorAll('input[name="skills"]');
        existingInputs.forEach(input => input.remove());
        
        const form = input.closest('form');
        if (form) {
            selectedSkills.forEach(skill => {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'skills';
                hiddenInput.value = skill;
                form.appendChild(hiddenInput);
            });
        }
    }
    
    // Add skill to selection
    function addSkill(skill) {
        if (selectedSkills.has(skill)) return;
        
        selectedSkills.add(skill);
        
        const skillTag = document.createElement('span');
        skillTag.className = 'skill-tag';
        skillTag.innerHTML = `
            ${skill}
            <button type="button" class="remove-skill" onclick="removeSkill('${skill}')">×</button>
        `;
        selectedSkillsContainer.appendChild(skillTag);
        
        updateHiddenInputs();
        input.value = '';
        dropdown.style.display = 'none';
    }
    
    // Remove skill from selection
    window.removeSkill = function(skill) {
        selectedSkills.delete(skill);
        const skillTags = selectedSkillsContainer.querySelectorAll('.skill-tag');
        skillTags.forEach(tag => {
            if (tag.textContent.includes(skill)) {
                tag.remove();
            }
        });
        updateHiddenInputs();
    };
    
    // Filter and show skills dropdown
    function showSkillsDropdown(query) {
        if (!query) {
            dropdown.style.display = 'none';
            return;
        }
        
        const filteredSkills = allSkills.filter(skill => 
            skill.toLowerCase().includes(query.toLowerCase()) && !selectedSkills.has(skill)
        );
        
        dropdown.innerHTML = '';
        
        if (filteredSkills.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        filteredSkills.slice(0, 10).forEach(skill => {
            const option = document.createElement('div');
            option.className = 'skill-option';
            option.textContent = skill;
            option.addEventListener('click', () => addSkill(skill));
            dropdown.appendChild(option);
        });
        
        dropdown.style.display = 'block';
    }
    
    // Event listeners
    input.addEventListener('input', function() {
        showSkillsDropdown(this.value);
    });
    
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const firstOption = dropdown.querySelector('.skill-option');
            if (firstOption) {
                addSkill(firstOption.textContent);
            }
        }
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!skillsContainer.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// Feedback System
function initializeFeedbackSystem() {
    const feedbackButtons = document.querySelectorAll('.feedback-btn');
    feedbackButtons.forEach(button => {
        button.addEventListener('click', function() {
            const rating = this.dataset.rating;
            submitFeedback(rating);
        });
    });
}

function submitFeedback(rating) {
    console.log('Feedback submitted:', rating);
    // Add feedback submission logic here
}

// Search Features
function initializeSearchFeatures() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            performSearch(this.value);
        });
    });
}

function performSearch(query) {
    console.log('Searching for:', query);
    // Add search logic here
}

// Tab Switching
function switchTab(tabId) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.style.display = 'none');
    
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabId).style.display = 'block';
    document.querySelector(`.tab-btn[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeApp();
});

// Global functions for HTML onclick handlers
window.switchTab = switchTab;
window.removeSkill = window.removeSkill || function() {};
