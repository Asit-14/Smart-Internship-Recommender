// Simple language test functions
function testLanguageDropdown() {
    console.log('Testing language dropdown...');
    
    const btn = document.getElementById('language-dropdown-btn');
    const dropdown = document.getElementById('language-dropdown');
    
    console.log('Button element:', btn);
    console.log('Dropdown element:', dropdown);
    
    if (btn && dropdown) {
        // Add simple test options
        dropdown.innerHTML = `
            <div class="dropdown-item" onclick="changeLanguageTest('en')">English</div>
            <div class="dropdown-item" onclick="changeLanguageTest('hi')">हिंदी</div>
            <div class="dropdown-item" onclick="changeLanguageTest('bn')">বাংলা</div>
            <div class="dropdown-item" onclick="changeLanguageTest('gu')">ગુજરાતી</div>
            <div class="dropdown-item" onclick="changeLanguageTest('ta')">தமிழ்</div>
        `;
        
        // Simple toggle
        btn.onclick = function() {
            console.log('Button clicked!');
            dropdown.classList.toggle('show');
        };
        
        console.log('Test dropdown setup complete');
    } else {
        console.error('Elements not found for testing');
    }
}

function changeLanguageTest(langCode) {
    console.log('Language changed to:', langCode);
    const currentLangText = document.getElementById('current-lang-text');
    const langNames = {
        'en': 'English',
        'hi': 'हिंदी', 
        'bn': 'বাংলা',
        'gu': 'ગુજરાતી',
        'ta': 'தமிழ்'
    };
    
    if (currentLangText) {
        currentLangText.textContent = langNames[langCode] || langCode;
    }
    
    // Close dropdown
    const dropdown = document.getElementById('language-dropdown');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
    
    // For now, just show an alert
    alert(`Language changed to: ${langNames[langCode]} (${langCode})`);
}

// Initialize test when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - setting up test');
    setTimeout(testLanguageDropdown, 500);
});
