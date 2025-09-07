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

// Initialize app
function initializeApp() {
    console.log('Initializing Smart Internship Recommender...');
    initializeSkillsSelector();
    initializeFormValidation();
    initializeFeedbackSystem();
    initializeSearchFeatures();
    console.log('Smart Internship Recommender initialized');
}

// Language switching functionality
function initializeLanguage() {
    console.log('Initializing language system...');
    
    // Get stored language preference
    currentLanguage = localStorage.getItem('preferredLanguage') || 'en';
    document.documentElement.lang = currentLanguage;
    
    // Update dropdown display
    updateLanguageDropdownDisplay();
    
    // Load and apply translations
    loadAndApplyTranslations(currentLanguage);
}

// Initialize language dropdown
function initializeLanguageDropdown() {
    console.log('Setting up language dropdown...');
    
    const dropdownBtn = document.getElementById('language-dropdown-btn');
    const dropdown = document.getElementById('language-dropdown');
    
    if (!dropdownBtn || !dropdown) {
        console.error('Language dropdown elements not found');
        return;
    }
    
    // Populate dropdown
    populateLanguageDropdown();
    
    // Add click handler
    dropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdownBtn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
    
    console.log('Language dropdown initialized');
}

// Populate language dropdown
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
}

// Switch to specific language
function switchToLanguage(langCode) {
    console.log(`Switching to language: ${langCode}`);
    
    currentLanguage = langCode;
    localStorage.setItem('preferredLanguage', langCode);
    document.documentElement.lang = langCode;
    
    // Handle RTL
    const langConfig = availableLanguages.find(lang => lang.code === langCode);
    if (langConfig && langConfig.rtl) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
    } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
    }
    
    // Update display
    updateLanguageDropdownDisplay();
    
    // Load translations
    loadAndApplyTranslations(langCode);
}

// Update language dropdown display
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

// Load and apply translations
function loadAndApplyTranslations(lang) {
    console.log(`Loading translations for: ${lang}`);
    
    fetch(`/static/locales/${lang}.json?t=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${lang}`);
            }
            return response.json();
        })
        .then(data => {
            translations = data;
            console.log(`Translations loaded for ${lang}`);
            applyTranslations();
        })
        .catch(error => {
            console.error('Error loading translations:', error);
        });
}

// Apply translations to elements
function applyTranslations() {
    if (!translations) return;
    
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const value = getNestedValue(translations, key);
        
        if (value) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.hasAttribute('placeholder')) {
                    element.setAttribute('placeholder', value);
                } else {
                    element.value = value;
                }
            } else {
                element.textContent = value;
            }
        }
    });
}

// Get nested object value by key path
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current && current[key], obj);
}

// Skills Selector
function initializeSkillsSelector() {
    const skillsContainer = document.getElementById('skills-container');
    if (!skillsContainer) return;
    
    const input = document.getElementById('skills-input');
    const dropdown = document.getElementById('skills-dropdown');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    const selectedSkills = new Set();
    
    // Basic skills
    let allSkills = ['Python', 'Java', 'JavaScript', 'HTML', 'CSS', 'SQL', 'Communication', 'Leadership', 'Teamwork', 'Problem Solving'];
    
    // Get skills from page data if available
    const skillsData = document.getElementById('skills-data');
    if (skillsData) {
        try {
            allSkills = JSON.parse(skillsData.textContent);
        } catch (e) {
            console.error('Error parsing skills data:', e);
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
    
    // Filter and show skills
    function showFilteredSkills(searchTerm) {
        dropdown.innerHTML = '';
        
        const filteredSkills = allSkills.filter(skill => 
            skill.toLowerCase().includes(searchTerm.toLowerCase()) && !selectedSkills.has(skill)
        );
        
        if (filteredSkills.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        filteredSkills.slice(0, 10).forEach(skill => {
            const skillElement = document.createElement('div');
            skillElement.className = 'skill-option';
            skillElement.textContent = skill;
            skillElement.addEventListener('click', () => addSkill(skill));
            dropdown.appendChild(skillElement);
        });
        
        dropdown.style.display = 'block';
    }
    
    // Add skill
    function addSkill(skill) {
        if (selectedSkills.has(skill)) return;
        
        selectedSkills.add(skill);
        
        const skillTag = document.createElement('span');
        skillTag.className = 'skill-tag';
        skillTag.innerHTML = `${skill} <button type="button" onclick="this.parentElement.remove(); updateSkills('${skill}', false)">&times;</button>`;
        selectedSkillsContainer.appendChild(skillTag);
        
        input.value = '';
        dropdown.style.display = 'none';
        updateHiddenInputs();
    }
    
    // Remove skill
    window.updateSkills = function(skill, add) {
        if (add) {
            selectedSkills.add(skill);
        } else {
            selectedSkills.delete(skill);
        }
        updateHiddenInputs();
    };
    
    // Input event
    input.addEventListener('input', function() {
        const searchTerm = this.value.trim();
        if (searchTerm.length > 0) {
            showFilteredSkills(searchTerm);
        } else {
            dropdown.style.display = 'none';
        }
    });
    
    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!skillsContainer.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add any validation logic here
        });
    });
}

// Feedback system
function initializeFeedbackSystem() {
    // Add feedback functionality if needed
}

// Search features  
function initializeSearchFeatures() {
    // Add search functionality if needed
}

// Tab switching
function switchTab(tabId) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.style.display = 'none');
    
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabId).style.display = 'block';
    document.querySelector(`.tab-btn[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

// Resume file handling
function initializeResumeUpload() {
    const fileInput = document.getElementById('resume-file');
    const fileLabel = document.querySelector('.file-upload-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Choose a file';
            }
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing app...');
    
    // Initialize main app
    initializeApp();
    
    // Initialize language system
    initializeLanguage();
    initializeLanguageDropdown();
    
    // Initialize other features
    initializeResumeUpload();
    
    console.log('All systems initialized');
});
