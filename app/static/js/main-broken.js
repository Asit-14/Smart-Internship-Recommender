/**
 * Main JavaScript file for the PM Internship Recommender
 * Enhanced with additional features for better user experience
 */

// Global variables
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeSkillsSelector();
    initializeFormValidation();
    // Language initialization is handled separately by DOMContentLoaded event
    initializeFeedbackSystem();
    initializeSearchFeatures();
    
    console.log('Smart Internship Recommender initialized');
}

// Enhanced Skills Selector
function initializeSkillsSelector() {
    const skillsContainer = document.getElementById('skills-container');
    if (!skillsContainer) return;
    
    const input = document.getElementById('skills-input');
    const dropdown = document.getElementById('skills-dropdown');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    const selectedSkills = new Set();
    
    // Get skills from translated data or fallback to page data
    let allSkills = [];
    if (window.translatedSkills && window.translatedSkills.length > 0) {
        allSkills = window.translatedSkills;
    } else {
        // Fallback to skills data from the page
        const skillsData = document.getElementById('skills-data');
        if (skillsData) {
            try {
                allSkills = JSON.parse(skillsData.textContent);
            } catch (e) {
                console.error('Error parsing skills data:', e);
                // Fallback to basic English skills
                allSkills = ['Python', 'Java', 'JavaScript', 'HTML', 'CSS', 'SQL', 'Communication', 'Leadership', 'Teamwork'];
            }
        }
    }
    
    // Create hidden inputs for the selected skills
    function updateHiddenInputs() {
        // Remove existing hidden inputs
        const existingInputs = document.querySelectorAll('input[name="skills"]');
        existingInputs.forEach(input => input.remove());
        
        // Add new hidden inputs
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
    
    // Add a skill chip
    function addSkill(skill) {
        if (selectedSkills.has(skill)) return;
        
        selectedSkills.add(skill);
        
        const chip = document.createElement('div');
        chip.className = 'skill-chip';
        chip.innerHTML = `
            ${skill}
            <span class="remove-skill" data-skill="${skill}">&times;</span>
        `;
        selectedSkillsContainer.appendChild(chip);
        
        // Add event listener to remove button
        const removeBtn = chip.querySelector('.remove-skill');
        removeBtn.addEventListener('click', function() {
            const skillToRemove = this.getAttribute('data-skill');
            selectedSkills.delete(skillToRemove);
            chip.remove();
            updateHiddenInputs();
        });
        
        updateHiddenInputs();
        input.value = '';
        dropdown.style.display = 'none';
    }
    
    // Filter and display skills
    function filterSkills(query) {
        if (!query) {
            dropdown.style.display = 'none';
            return;
        }
        
        const filtered = allSkills.filter(skill => 
            skill.toLowerCase().includes(query.toLowerCase()) &&
            !selectedSkills.has(skill)
        );
        
        dropdown.innerHTML = '';
        
        if (filtered.length > 0) {
            filtered.slice(0, 10).forEach(skill => {
                const option = document.createElement('div');
                option.className = 'skill-option';
                option.textContent = skill;
                option.addEventListener('click', () => addSkill(skill));
                dropdown.appendChild(option);
            });
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    }
    
    // Event listeners
    if (input) {
        input.addEventListener('input', function() {
            filterSkills(this.value);
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const firstOption = dropdown.querySelector('.skill-option');
                if (firstOption) {
                    addSkill(firstOption.textContent);
                } else if (this.value.trim()) {
                    addSkill(this.value.trim());
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
}

// Initialize file upload component
function initializeFileUpload() {
    const fileInput = document.getElementById('resume');
    const fileLabel = document.getElementById('file-name');
    
    if (!fileInput || !fileLabel) return;
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileLabel.textContent = this.files[0].name;
        } else {
            fileLabel.textContent = 'Choose a file';
        }
    });
}

// Switch between tabs
function switchTab(tabId) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.style.display = 'none');
    
    // Deactivate all tabs
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab content and activate tab
    document.getElementById(tabId).style.display = 'block';
    document.querySelector(`.tab-btn[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

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

// Language switching functionality
function initializeLanguage() {
    console.log('Starting language initialization...');
    
    // Get the stored language preference
    currentLanguage = localStorage.getItem('preferredLanguage') || 'en';
    
    console.log(`Initializing with language: ${currentLanguage}`);
    
    // Set the HTML lang attribute
    document.documentElement.lang = currentLanguage;
    
    // Load skills data first
    loadLanguageConfig().then(() => {
        console.log('Language config loaded, proceeding with initialization...');
        
        // Update the dropdown display
        updateLanguageDropdownDisplay();
        
        // Load and apply translations
        loadAndApplyTranslations(currentLanguage);
        
        // Load skills data for current language
        loadSkillsData(currentLanguage);
        
        console.log('Language initialization completed');
    }).catch(error => {
        console.error('Failed to initialize language:', error);
        // Continue with basic functionality even if config fails
        updateLanguageDropdownDisplay();
        loadAndApplyTranslations(currentLanguage);
    });
}

// Load language configuration
function loadLanguageConfig() {
    console.log('Loading language configuration...');
    return fetch('/static/locales/languages.json?t=' + new Date().getTime())
        .then(response => {
            console.log('Language config response status:', response.status);
            if (!response.ok) {
                throw new Error('Failed to load language configuration');
            }
            return response.json();
        })
        .then(data => {
            console.log('Language config data received:', data);
            availableLanguages = data.languages;
            skillsData = data.skills;
            console.log('Loaded language configuration:', availableLanguages.length, 'languages');
            console.log('Available languages list:', availableLanguages.map(l => l.code));
            return data;
        })
        .catch(error => {
            console.error('Error loading language configuration:', error);
            // Fallback to basic English/Hindi if config fails
            availableLanguages = [
                { code: 'en', name: 'English', nativeName: 'English', rtl: false },
                { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', rtl: false },
                { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', rtl: false },
                { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', rtl: false },
                { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', rtl: false }
            ];
            skillsData = {
                'en': ['Python', 'Java', 'JavaScript', 'Communication', 'Leadership'],
                'hi': ['पायथन', 'जावा', 'जावास्क्रिप्ट', 'संचार', 'नेतृत्व'],
                'bn': ['পাইথন', 'জাভা', 'জাভাস্ক্রিপ্ট', 'যোগাযোগ', 'নেতৃত্ব'],
                'gu': ['પાયથન', 'જાવા', 'જાવાસ્ક્રિપ્ટ', 'સંચાર', 'નેતૃત્વ'],
                'ta': ['பைத்தான்', 'ஜாவா', 'ஜாவாஸ்கிரிப்ட்', 'தகவல் பரிमाற்சम్', 'தলैमాத্વম्']
            };
            console.log('Using fallback language configuration');
            return Promise.resolve();
        });
}

// Load skills data for a specific language
function loadSkillsData(langCode) {
    if (skillsData && skillsData[langCode]) {
        // Update the skills in the dropdown
        updateSkillsDropdown(skillsData[langCode]);
    } else {
        // Fallback to English if language not found
        updateSkillsDropdown(skillsData['en'] || []);
    }
}

// Update skills dropdown with translated skills
function updateSkillsDropdown(skills) {
    // This will be used by the skills selector initialization
    window.translatedSkills = skills;
    
    // If skills selector is already initialized, update it
    const skillsContainer = document.getElementById('skills-container');
    if (skillsContainer && skills.length > 0) {
        // Re-initialize skills with new language data
        setTimeout(() => {
            initializeSkillsSelector();
        }, 100);
    }
}
    fetch(`/static/locales/${lang}.json?t=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${lang}`);
            }
            return response.json();
        })
        .then(data => {
            translations = data;
            console.log(`Loaded translations for ${lang}:`, Object.keys(translations));
            applyTranslations();
        })
        .catch(error => {
            console.error('Error loading translations:', error);
        });
}

// Apply translations to all elements with data-i18n attribute
function applyTranslations() {
    if (!translations || Object.keys(translations).length === 0) {
        console.error('No translations available');
        return;
    }
    
    const elements = document.querySelectorAll('[data-i18n]');
    console.log(`Found ${elements.length} elements with data-i18n attributes`);
    
    elements.forEach(element => {
        try {
            const key = element.getAttribute('data-i18n');
            const parts = key.split('.');
            
            // Navigate through the translation object
            let value = translations;
            for (const part of parts) {
                if (!value || !value[part]) {
                    console.warn(`Translation key not found: ${key}`);
                    return;
                }
                value = value[part];
            }
            
            // Apply the translation based on element type
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

// Toggle between languages
function toggleLanguage() {
    // This function is kept for backwards compatibility
    // but now we use the dropdown instead
    const nextLang = currentLanguage === 'en' ? 'hi' : 'en';
    switchToLanguage(nextLang);
}

// Switch to a specific language
function switchToLanguage(langCode) {
    console.log(`Switching language to: ${langCode}`);
    
    // Update current language
    currentLanguage = langCode;
    
    // Save the preference
    localStorage.setItem('preferredLanguage', langCode);
    console.log(`Language preference saved: ${langCode}`);
    
    // Set HTML direction for RTL languages
    const langConfig = availableLanguages.find(lang => lang.code === langCode);
    if (langConfig && langConfig.rtl) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
        console.log('RTL mode enabled');
    } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
        console.log('LTR mode enabled');
    }
    
    // Update the HTML lang attribute
    document.documentElement.lang = langCode;
    
    // Update dropdown display
    updateLanguageDropdownDisplay();
    
    // Load and apply translations
    loadAndApplyTranslations(langCode);
    
    // Load skills data for new language
    loadSkillsData(langCode);
    
    console.log(`Language switch to ${langCode} completed`);
}

// Initialize language dropdown
function initializeLanguageDropdown() {
    console.log('Initializing language dropdown...');
    const dropdownBtn = document.getElementById('language-dropdown-btn');
    const dropdown = document.getElementById('language-dropdown');
    
    if (!dropdownBtn || !dropdown) {
        console.error('Language dropdown elements not found:', {
            dropdownBtn: !!dropdownBtn,
            dropdown: !!dropdown
        });
        return;
    }
    
    console.log('Language dropdown elements found successfully');
    
    // Populate dropdown with available languages
    populateLanguageDropdown();
    
    // Toggle dropdown on button click
    dropdownBtn.addEventListener('click', function(e) {
        console.log('Language dropdown button clicked');
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.toggle('show');
        console.log('Dropdown show class toggled:', dropdown.classList.contains('show'));
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdownBtn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
    
    console.log('Language dropdown initialized successfully');
}

// Populate language dropdown with available languages
function populateLanguageDropdown() {
    console.log('Populating language dropdown...');
    const dropdown = document.getElementById('language-dropdown');
    if (!dropdown) {
        console.error('Language dropdown element not found for population');
        return;
    }
    
    if (!availableLanguages || availableLanguages.length === 0) {
        console.error('No available languages to populate');
        return;
    }
    
    console.log('Available languages:', availableLanguages.length, availableLanguages);
    
    dropdown.innerHTML = '';
    
    availableLanguages.forEach((lang, index) => {
        console.log(`Adding language option ${index + 1}:`, lang);
        const option = document.createElement('div');
        option.className = 'dropdown-item';
        option.textContent = `${lang.nativeName} (${lang.name})`;
        option.dataset.langCode = lang.code;
        
        if (lang.code === currentLanguage) {
            option.classList.add('active');
            console.log(`Set ${lang.code} as active option`);
        }
        
        option.addEventListener('click', function(e) {
            console.log(`Language option clicked: ${lang.code}`);
            e.preventDefault();
            switchToLanguage(lang.code);
            dropdown.classList.remove('show');
        });
        
        dropdown.appendChild(option);
    });
    
    console.log(`Language dropdown populated with ${availableLanguages.length} options`);
}

// Update language dropdown display
function updateLanguageDropdownDisplay() {
    const currentLangText = document.getElementById('current-lang-text');
    if (!currentLangText || !availableLanguages.length) return;
    
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

