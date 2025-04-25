/**
 * Main JavaScript file for the Creative Text Generator application
 */

// Global application settings
const appSettings = {
    // Default settings
    defaultLanguage: 'English',
    defaultLevel: 'B1-B2',
    saveHistory: true,
    temperature: 0.7,
    topP: 0.9,
    maxRetries: 3,
    fontSize: 16,
    theme: 'light',
    
    // Load settings from localStorage
    load: function() {
        const savedSettings = localStorage.getItem('appSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            Object.assign(this, settings);
        }
        return this;
    },
    
    // Save settings to localStorage
    save: function() {
        localStorage.setItem('appSettings', JSON.stringify({
            defaultLanguage: this.defaultLanguage,
            defaultLevel: this.defaultLevel,
            saveHistory: this.saveHistory,
            temperature: this.temperature,
            topP: this.topP,
            maxRetries: this.maxRetries,
            fontSize: this.fontSize,
            theme: this.theme
        }));
        return this;
    },
    
    // Apply settings to the UI
    apply: function() {
        // Apply theme
        if (this.theme === 'dark') {
            $('body').addClass('dark-theme');
        } else {
            $('body').removeClass('dark-theme');
        }
        
        // Apply font size
        document.documentElement.style.setProperty('--text-font-size', `${this.fontSize}px`);
        
        return this;
    }
};

// Global application state
const appState = {
    // Current text/story data
    currentTextData: null,
    currentStoryData: null,
    
    // Set current text data
    setTextData: function(data) {
        this.currentTextData = data;
        return this;
    },
    
    // Set current story data
    setStoryData: function(data) {
        this.currentStoryData = data;
        return this;
    },
    
    // Clear current text data
    clearTextData: function() {
        this.currentTextData = null;
        return this;
    },
    
    // Clear current story data
    clearStoryData: function() {
        this.currentStoryData = null;
        return this;
    }
};

// Custom alert function
function showCustomAlert(message, type = 'info') {
    // Remove any existing alerts
    $('.custom-alert').remove();
    
    // Create alert element
    const alertHtml = `
        <div class="custom-alert alert alert-${type} alert-dismissible fade show">
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add alert to the page
    $('body').append(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.custom-alert').alert('close');
    }, 5000);
}

// Copy text to clipboard
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text)
        .then(() => {
            showCustomAlert('Text copied to clipboard!', 'success');
            return true;
        })
        .catch(() => {
            showCustomAlert('Failed to copy text. Please try again.', 'danger');
            return false;
        });
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Show loading overlay
function showLoading(message = 'Loading...') {
    $('#loadingOverlay').removeClass('d-none');
    $('#loadingMessage').text(message);
}

// Hide loading overlay
function hideLoading() {
    $('#loadingOverlay').addClass('d-none');
}

// Get language options HTML excluding a specific language
function getLanguageOptionsHtml(excludedLanguage = null) {
    const languages = [
        "English", "Turkish", "German", "French", "Spanish",
        "Italian", "Dutch", "Russian", "Portuguese", "Japanese"
    ];
    
    return languages.map(lang => {
        const disabled = lang === excludedLanguage ? 'disabled' : '';
        const selected = lang !== excludedLanguage ? 'selected' : '';
        return `<option value="${lang}" ${disabled} ${selected}>${lang}</option>`;
    }).join('');
}

// Initialize application
$(document).ready(function() {
    // Load and apply settings
    appSettings.load().apply();
    
    // Initialize any global components
    initializeGlobalComponents();
});

// Initialize global components
function initializeGlobalComponents() {
    // Settings modal functionality
    $('#temperature').on('input', function() {
        $('#temperatureValue').text($(this).val());
    });
    
    $('#topP').on('input', function() {
        $('#topPValue').text($(this).val());
    });
    
    $('#fontSize').on('input', function() {
        $('#fontSizeValue').text($(this).val());
    });
    
    // Save settings
    $('#saveSettings').click(function() {
        appSettings.defaultLanguage = $('#defaultLanguage').val();
        appSettings.defaultLevel = $('#defaultLevel').val();
        appSettings.saveHistory = $('#saveHistory').prop('checked');
        appSettings.temperature = parseFloat($('#temperature').val());
        appSettings.topP = parseFloat($('#topP').val());
        appSettings.maxRetries = parseInt($('#maxRetries').val());
        appSettings.fontSize = parseInt($('#fontSize').val());
        appSettings.theme = $('#theme').val();
        
        // Save and apply settings
        appSettings.save().apply();
        
        // Close modal
        $('#settingsModal').modal('hide');
        
        // Show success message
        showCustomAlert('Settings saved successfully!', 'success');
    });
    
    // Load settings into modal when opened
    $('#settingsModal').on('show.bs.modal', function() {
        $('#defaultLanguage').val(appSettings.defaultLanguage);
        $('#defaultLevel').val(appSettings.defaultLevel);
        $('#saveHistory').prop('checked', appSettings.saveHistory);
        $('#temperature').val(appSettings.temperature);
        $('#temperatureValue').text(appSettings.temperature);
        $('#topP').val(appSettings.topP);
        $('#topPValue').text(appSettings.topP);
        $('#maxRetries').val(appSettings.maxRetries);
        $('#fontSize').val(appSettings.fontSize);
        $('#fontSizeValue').text(appSettings.fontSize);
        $('#theme').val(appSettings.theme);
    });
}