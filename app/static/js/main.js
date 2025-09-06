/**
 * Main JavaScript file for the PM Internship Recommender
 */

// Initialize skills selector component
function initializeSkillsSelector(allSkills) {
    const input = document.getElementById('skills-input');
    const dropdown = document.getElementById('skills-dropdown');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    const selectedSkills = new Set();
    
    // Create hidden inputs for the selected skills
    function updateHiddenInputs() {
        // Remove existing hidden inputs
        const existingInputs = document.querySelectorAll('input[name="skills"]');
        existingInputs.forEach(input => input.remove());
        
        // Add new hidden inputs
        const form = input.closest('form');
        selectedSkills.forEach(skill => {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'skills';
            hiddenInput.value = skill;
            form.appendChild(hiddenInput);
        });
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
    }
    
    // Show dropdown with matching skills
    function showDropdown(query) {
        dropdown.innerHTML = '';
        
        const matchingSkills = allSkills.filter(skill => 
            skill.toLowerCase().includes(query.toLowerCase()) && !selectedSkills.has(skill)
        );
        
        if (matchingSkills.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        matchingSkills.forEach(skill => {
            const option = document.createElement('div');
            option.className = 'skill-option';
            option.textContent = skill;
            option.addEventListener('click', function() {
                addSkill(skill);
                input.value = '';
                dropdown.style.display = 'none';
            });
            dropdown.appendChild(option);
        });
        
        dropdown.style.display = 'block';
    }
    
    // Handle input changes
    input.addEventListener('input', function() {
        const query = this.value.trim();
        if (query) {
            showDropdown(query);
        } else {
            dropdown.style.display = 'none';
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!input.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.style.display = 'none';
        }
    });
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

// Initialize voice input component
function initializeVoiceInput() {
    const startVoiceBtn = document.getElementById('start-voice');
    const voiceResult = document.getElementById('voice-result');
    const voiceText = document.getElementById('voice-text');
    const voiceFormData = document.getElementById('voice-form-data');
    const voiceSubmitBtn = document.getElementById('voice-submit');
    const voiceRetryBtn = document.getElementById('voice-retry');
    const voiceStatus = document.getElementById('voice-status');
    
    if (!startVoiceBtn) return;
    
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        startVoiceBtn.textContent = 'Voice input not supported in your browser';
        startVoiceBtn.disabled = true;
        if (voiceStatus) {
            voiceStatus.innerHTML = '<div class="error-message">Speech recognition is not supported in your browser. Please use Chrome for best results.</div>';
        }
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN'; // Default to English (India)
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Function to start voice recognition
    function startVoiceRecognition() {
        startVoiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Listening...</span>';
        startVoiceBtn.classList.add('listening');
        if (voiceStatus) {
            voiceStatus.innerHTML = '<div class="listening-message">Listening... Speak now</div>';
        }
        try {
            recognition.start();
        } catch (e) {
            console.error('Error starting speech recognition:', e);
            resetVoiceUI();
            if (voiceStatus) {
                voiceStatus.innerHTML = '<div class="error-message">Could not start speech recognition. Please try again.</div>';
            }
        }
    }
    
    // Reset UI elements
    function resetVoiceUI() {
        startVoiceBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Tap to Speak</span>';
        startVoiceBtn.classList.remove('listening');
        if (voiceStatus) {
            voiceStatus.innerHTML = '';
        }
    }
    
    // Event listeners for speech recognition
    startVoiceBtn.addEventListener('click', startVoiceRecognition);
    
    // Add retry functionality
    if (voiceRetryBtn) {
        voiceRetryBtn.addEventListener('click', function() {
            voiceResult.style.display = 'none';
            startVoiceRecognition();
        });
    }
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        voiceText.textContent = transcript;
        voiceResult.style.display = 'block';
        
        // Process the voice input
        processVoiceInput(transcript);
    };
    
    recognition.onend = function() {
        resetVoiceUI();
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
        resetVoiceUI();
        
        if (voiceStatus) {
            voiceStatus.innerHTML = `<div class="error-message">Error: ${event.error}. Please try again.</div>`;
        }
    };
    
    // Store extracted data for form submission
    let extractedData = {
        sector: '',
        location: '',
        skills: []
    };
    
    // Process voice input
    function processVoiceInput(text) {
        // Send to backend for processing
        fetch('/voice-input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Store the extracted data
            extractedData = {
                sector: data.sector || '',
                location: data.location || '',
                skills: data.skills || []
            };
            
            // Display extracted data
            let formDataHtml = '';
            
            if (data.sector) {
                formDataHtml += `<div class="extracted-data"><strong>Sector:</strong> ${data.sector}</div>`;
            }
            
            if (data.location) {
                formDataHtml += `<div class="extracted-data"><strong>Location:</strong> ${data.location}</div>`;
            }
            
            if (data.skills && data.skills.length > 0) {
                formDataHtml += `<div class="extracted-data"><strong>Skills:</strong> ${data.skills.join(', ')}</div>`;
            }
            
            if (!formDataHtml) {
                formDataHtml = '<div>Could not extract specific details. Please try again with more specific information or use the form.</div>';
            }
            
            voiceFormData.innerHTML = formDataHtml;
        })
        .catch(error => {
            console.error('Error:', error);
            voiceFormData.innerHTML = '<div>Error processing voice input. Please try again or use the form.</div>';
        });
    }
    
    // Submit voice form
    voiceSubmitBtn.addEventListener('click', function() {
        if (!extractedData.sector && !extractedData.location && (!extractedData.skills || extractedData.skills.length === 0)) {
            alert('Please provide more specific information through voice input or use the form.');
            return;
        }
        
        // Create a form dynamically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/form-submit';
        form.style.display = 'none';
        
        // Add the sector input
        if (extractedData.sector) {
            const sectorInput = document.createElement('input');
            sectorInput.type = 'hidden';
            sectorInput.name = 'sector';
            sectorInput.value = extractedData.sector;
            form.appendChild(sectorInput);
        }
        
        // Add the location input
        if (extractedData.location) {
            const locationInput = document.createElement('input');
            locationInput.type = 'hidden';
            locationInput.name = 'location';
            locationInput.value = extractedData.location;
            form.appendChild(locationInput);
        }
        
        // Add the skills inputs
        if (extractedData.skills && extractedData.skills.length > 0) {
            extractedData.skills.forEach(skill => {
                const skillInput = document.createElement('input');
                skillInput.type = 'hidden';
                skillInput.name = 'skills';
                skillInput.value = skill;
                form.appendChild(skillInput);
            });
        }
        
        // Add default education (this can be improved in a real app)
        const educationInput = document.createElement('input');
        educationInput.type = 'hidden';
        educationInput.name = 'education';
        educationInput.value = 'Graduate';  // Default value
        form.appendChild(educationInput);
        
        // Append the form to the body and submit it
        document.body.appendChild(form);
        form.submit();
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

// Toggle between languages
function toggleLanguage() {
    const langBtn = document.getElementById('lang-toggle');
    const currentLang = langBtn.querySelector('#lang-text').textContent;
    
    if (currentLang === 'हिंदी') {
        // Switch to Hindi (in a real app, this would load Hindi translations)
        langBtn.querySelector('#lang-text').textContent = 'English';
        alert('Hindi language support is not implemented in this demo version.');
    } else {
        // Switch back to English
        langBtn.querySelector('#lang-text').textContent = 'हिंदी';
    }
}
