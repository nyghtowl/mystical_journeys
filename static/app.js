/**
 * Main application class for the Mystical Journeys travel planner interface.
 * 
 * This class manages the entire frontend experience including:
 * - Form submission and validation
 * - Real-time streaming from multiple AI providers
 * - Fantasy theme language switching (Dragon emoji mode)
 * - Responsive UI updates and error handling
 * - Provider comparison and booking workflow
 * 
 * The app uses a single-page design with three main sections:
 * 1. Travel form (quest selection)
 * 2. Loading state (consulting oracles)
 * 3. Results comparison (oracle responses)
 */
class TravelPlannerApp {
    constructor() {
        // Core DOM elements for the three main application sections
        this.form = document.getElementById('travelForm');
        this.travelFormSection = document.getElementById('travel-form');
        this.loadingSection = document.getElementById('loading');
        this.resultsSection = document.getElementById('results');
        this.comparisonContainer = document.getElementById('comparison-container');
        
        // Initialize all event handlers and UI components
        this.init();
    }

    init() {
        console.log('Form element found:', this.form);
        console.log('Form sections:', {
            travelFormSection: this.travelFormSection,
            loadingSection: this.loadingSection,
            resultsSection: this.resultsSection
        });
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                console.log('Form submit event triggered');
                e.preventDefault();
                e.stopPropagation();
                this.handleSubmit(e);
            });
            console.log('Submit event listener added');
            
            // Also add a direct click listener to the button as backup
            const submitBtn = this.form.querySelector('button[type="submit"]');
            console.log('Submit button found:', submitBtn);
            if (submitBtn) {
                // Make sure button is not disabled
                submitBtn.disabled = false;
                submitBtn.addEventListener('click', (e) => {
                    console.log('Button clicked directly');
                    // Don't prevent the click - let it bubble up to trigger form submit
                    console.log('Button click will trigger form submit');
                });
            } else {
                console.error('Submit button not found!');
            }
        } else {
            console.error('Form element not found!');
        }
        this.addFormValidation();
        this.addBackToFormHandler();
        this.addResetHandler();
        this.initializeLanguageSelector();
        this.storeOriginalContent();
    }

    addFormValidation() {
        // Clear field errors when user starts typing/selecting
        const inputs = this.form.querySelectorAll('select, textarea, input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.clearFieldError(input.name);
            });
            input.addEventListener('change', () => {
                this.clearFieldError(input.name);
            });
        });
    }

    addResetHandler() {
        // Make company name clickable to reset to original form
        const companyName = document.getElementById('main-title');
        if (companyName) {
            companyName.addEventListener('click', () => {
                this.resetToOriginalForm();
            });
        }
    }

    resetToOriginalForm() {
        // Reset form
        if (this.form) {
            this.form.reset();
        }
        
        // Clear any error states
        document.querySelectorAll('.form-group.error').forEach(group => {
            group.classList.remove('error');
        });
        document.querySelectorAll('.error-message.show').forEach(error => {
            error.classList.remove('show');
        });
        
        // Show form section, hide others
        if (this.travelFormSection) this.travelFormSection.style.display = 'block';
        if (this.loadingSection) this.loadingSection.style.display = 'none';
        if (this.resultsSection) this.resultsSection.style.display = 'none';
        
        // Scroll to top smoothly
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        console.log('Form reset to original state');
    }

    addBackToFormHandler() {
        // Add click handler for back to form button (using event delegation)
        document.addEventListener('click', (e) => {
            if (e.target.id === 'back-to-form-btn' || e.target.closest('#back-to-form-btn')) {
                this.resetToOriginalForm();
            }
        });
    }

    showForm() {
        // Hide results and loading sections
        this.resultsSection.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        
        // Show the form section
        this.travelFormSection.classList.remove('hidden');
        
        // Scroll to the form
        this.travelFormSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        // Add a subtle animation
        this.travelFormSection.style.animation = 'fadeIn 0.5s ease-in';
        setTimeout(() => {
            if (this.travelFormSection.style) {
                this.travelFormSection.style.animation = '';
            }
        }, 500);
    }

    async handleSubmit(e) {
        console.log('handleSubmit called with event:', e);
        e.preventDefault();
        e.stopPropagation();
        console.log('Form submitted!');
        
        try {
            const formData = new FormData(this.form);
            const travelData = this.extractFormData(formData);
            console.log('Travel data:', travelData);

            if (!this.validateForm(travelData)) {
                console.log('Form validation failed');
                return;
            }

            console.log('Validation passed, showing loading...');
            this.showLoading();
            await this.generateItinerary(travelData);
        } catch (error) {
            console.error('Error in form submission:', error);
            // Show error to user
            alert('There was an error submitting the form. Please try again.');
        }
    }

    extractFormData(formData) {
        const providers = formData.getAll('providers');
        return {
            destination: formData.get('destination'),
            days: parseInt(formData.get('days')) || 5,
            budget: formData.get('budget'),
            interests: formData.getAll('interests'),
            providers: providers
        };
    }

    validateForm(data) {
        // Clear previous errors
        this.clearFormErrors();
        
        let hasErrors = false;
        
        // Validate destination
        if (!data.destination || !data.destination.trim()) {
            this.showFieldError('destination', 'Please select a mystical realm to explore!');
            hasErrors = true;
        }

        // Validate days
        if (!data.days || data.days < 1 || data.days > 30) {
            this.showFieldError('days', 'Please enter a valid quest duration (1-30 days)!');
            hasErrors = true;
        }

        // Validate budget
        if (!data.budget || !data.budget.trim()) {
            this.showFieldError('budget', 'Please set your treasure budget!');
            hasErrors = true;
        }

        // Validate interests (at least one must be selected)
        if (!data.interests || data.interests.length === 0) {
            this.showFieldError('interests', 'Please select at least one quest interest!');
            hasErrors = true;
        }

        // Validate providers
        if (!data.providers || data.providers.length === 0) {
            this.showFieldError('providers', 'Please select at least one AI oracle to consult!');
            hasErrors = true;
        }
        
        // If there are errors, scroll to the first error field
        if (hasErrors) {
            const firstError = document.querySelector('.form-group.error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        return !hasErrors;
    }
    
    showFieldError(fieldName, message) {
        let fieldGroup;
        
        // Handle special cases for fields without single IDs
        if (fieldName === 'interests') {
            // Find the interests fieldset by looking for checkbox inputs with name="interests"
            const interestsInput = document.querySelector('input[name="interests"]');
            fieldGroup = interestsInput ? interestsInput.closest('.form-group') : null;
        } else if (fieldName === 'providers') {
            // Find the providers fieldset by looking for checkbox inputs with name="providers"
            const providersInput = document.querySelector('input[name="providers"]');
            fieldGroup = providersInput ? providersInput.closest('.form-group') : null;
        } else {
            // Regular fields with IDs
            const fieldElement = document.getElementById(fieldName);
            fieldGroup = fieldElement ? fieldElement.closest('.form-group') : null;
        }
        
        if (!fieldGroup) {
            console.error(`Could not find form group for field: ${fieldName}`);
            return;
        }
        
        const errorElement = fieldGroup.querySelector('.error-message');
        
        // Add error styling to form group
        fieldGroup.classList.add('error');
        
        // Show error message
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }
    
    clearFormErrors() {
        const formGroups = this.form.querySelectorAll('.form-group.error');
        formGroups.forEach(group => {
            group.classList.remove('error');
            const errorMsg = group.querySelector('.error-message.show');
            if (errorMsg) {
                errorMsg.classList.remove('show');
            }
        });
    }

    clearFieldError(fieldName) {
        let fieldGroup;
        
        // Handle special cases for fields without single IDs
        if (fieldName === 'interests') {
            const interestsInput = document.querySelector('input[name="interests"]');
            fieldGroup = interestsInput ? interestsInput.closest('.form-group') : null;
        } else if (fieldName === 'providers') {
            const providersInput = document.querySelector('input[name="providers"]');
            fieldGroup = providersInput ? providersInput.closest('.form-group') : null;
        } else {
            const fieldElement = document.getElementById(fieldName);
            fieldGroup = fieldElement ? fieldElement.closest('.form-group') : null;
        }
        
        if (fieldGroup && fieldGroup.classList.contains('error')) {
            fieldGroup.classList.remove('error');
            const errorMsg = fieldGroup.querySelector('.error-message.show');
            if (errorMsg) {
                errorMsg.classList.remove('show');
            }
        }
    }

    showLoading() {
        // Create sparkle animation
        this.createSparkleAnimation();
        
        // After sparkle animation, hide form and show loading
        setTimeout(() => {
            this.travelFormSection.classList.add('hidden');
            this.loadingSection.classList.remove('hidden');
        }, 1800);
    }

    hideLoading() {
        this.loadingSection.classList.add('hidden');
    }
    
    createSparkleAnimation() {
        const sparkleContainer = document.getElementById('sparkle-container');
        
        // Create many sparkles with variety
        const sparkleEmojis = ['✨', '🌟', '⭐', '💫', '✨', '🌟', '⭐', '💫', '✨', '🌟', '⭐', '💫', '✨', '🌟', '⭐', '💫', '✨', '🌟', '⭐', '💫'];
        sparkleEmojis.forEach((emoji, index) => {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.textContent = emoji;
            
            // Random positioning
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.top = Math.random() * 100 + '%';
            
            sparkleContainer.appendChild(sparkle);
        });
        
        // Remove sparkles after animation
        setTimeout(() => {
            sparkleContainer.innerHTML = '';
        }, 2500);
    }
    
    showResults() {
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.remove('hidden');
    }
    




    async generateItinerary(travelData) {
        try {
            const response = await fetch('/generate-comparison', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(travelData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            await this.handleComparisonResponse(response);
            
        } catch (error) {
            console.error('Error generating itinerary:', error);
            
            // Check if it's an API key error
            if (error.message.includes('API key') || error.message.includes('401')) {
                this.showError('🔑 Oracle Connection Missing! The mystical AI spirits require an API key to weave your tale.');
            } else {
                this.showError('⚠️ The oracle encountered a disturbance! Please try your quest again.');
            }
        } finally {
            this.showResults();
        }
    }

    async handleComparisonResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        this.comparisonContainer.innerHTML = '';
        let buffer = '';
        const oraclePanels = {};
        
        // Add timeout to prevent getting stuck
        const timeout = setTimeout(() => {
            console.warn('Streaming response timeout - finishing comparison');
            this.finishComparison();
        }, 60000); // 60 second timeout

        try {
            console.log('Starting to handle streaming response...');
            let chunkCount = 0;
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    console.log('Stream completed, received', chunkCount, 'chunks');
                    break;
                }

                chunkCount++;
                console.log('Received chunk', chunkCount, 'with', value.length, 'bytes');
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            console.log('Parsed streaming data:', data);
                            
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            
                            if (data.providers) {
                                console.log('Setting up comparison panels for providers:', data.providers);
                                this.setupComparisonPanels(data.providers);
                            }
                            
                            if (data.provider && data.result) {
                                console.log('Updating panel for provider:', data.provider);
                                this.updateOraclePanel(data.provider, data.result, false);
                            }
                            
                            if (data.provider && data.error) {
                                console.log('Updating panel with error for provider:', data.provider);
                                this.updateOraclePanel(data.provider, data.error, true);
                            }
                            
                            if (data.done) {
                                console.log('Received done signal, finishing comparison');
                                clearTimeout(timeout);
                                this.finishComparison();
                                return;
                            }
                        } catch (parseError) {
                            console.warn('Failed to parse comparison data:', parseError, 'Line:', line);
                        }
                    }
                }
            }
            
            // If we exit the loop without getting a done signal, finish anyway
            console.log('Stream ended without done signal, finishing comparison');
            clearTimeout(timeout);
            this.finishComparison();
            
        } catch (error) {
            clearTimeout(timeout);
            console.error('Error in handleComparisonResponse:', error);
            throw error;
        }
    }

    appendContent(content) {
        // Remove any existing cursor
        this.itineraryContent.classList.remove('streaming-text');
        
        // Append new content
        this.itineraryContent.innerHTML += this.formatContent(content);
        
        // Add streaming cursor
        this.itineraryContent.classList.add('streaming-text');
        
        // Scroll to bottom
        this.itineraryContent.scrollTop = this.itineraryContent.scrollHeight;
    }

    formatContent(content, providerKey = null) {
        // Modern fantasy-themed formatting for better readability
        const formattedContent = content
            .replace(/\n\n/g, '</p><p class="mb-4 text-gray-700">')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-700 font-bold">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="text-gray-600 italic">$1</em>')
            .replace(/Day (\d+)/g, '<h3 class="text-xl font-bold text-purple-700 mt-6 mb-3 flex items-center border-b border-purple-200 pb-2"><span class="text-2xl mr-2">📜</span>Quest Day $1</h3>')
            .replace(/Chapter (\d+)/g, '<h3 class="text-xl font-bold text-purple-700 mt-6 mb-3 flex items-center border-b border-purple-200 pb-2"><span class="text-2xl mr-2">📖</span>Chapter $1</h3>');
        
        // Add booking button if providerKey is provided
        const bookingButton = providerKey ? `
            <div class="booking-actions">
                <button class="book-quest-btn" onclick="window.app.bookItinerary('${providerKey}', this)">
                    📜 Book This Quest
                </button>
            </div>
        ` : '';
        
        return formattedContent + bookingButton;
    }

    setupComparisonPanels(providers) {
        const panelCount = providers.length;
        this.comparisonContainer.className = `comparison-container ${
            panelCount === 2 ? 'split' : panelCount === 3 ? 'triple' : ''
        }`;
        
        providers.forEach(providerKey => {
            const panel = this.createOraclePanel(providerKey);
            this.comparisonContainer.appendChild(panel);
        });
    }
    
    createOraclePanel(providerKey) {
        const providerNames = {
            'openai': 'OpenAI GPT-3.5 Turbo',
            'ollama': 'Ollama DeepSeek-R1',
            'claude': 'Claude 3.5 Sonnet'
        };
        
        const panel = document.createElement('div');
        panel.className = 'oracle-panel loading';
        panel.id = `panel-${providerKey}`;
        
        panel.innerHTML = `
            <div class="oracle-header">
                <div class="oracle-name">
                    <i class="fas fa-crystal-ball"></i>
                    ${providerNames[providerKey] || providerKey}
                </div>
                <div class="oracle-status loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Consulting...
                </div>
            </div>
            <div class="oracle-content">
                <div class="oracle-loading">
                    <div class="oracle-spinner"></div>
                    <p>The oracle is weaving your tale...</p>
                </div>
            </div>
        `;
        
        return panel;
    }
    
    updateOraclePanel(providerKey, content, isError = false) {
        const panel = document.getElementById(`panel-${providerKey}`);
        if (!panel) return;
        
        const status = panel.querySelector('.oracle-status');
        const contentDiv = panel.querySelector('.oracle-content');
        
        if (isError) {
            panel.className = 'oracle-panel error';
            status.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Unavailable';
            
            // Clean up error messages that start with "Error: "
            const cleanError = content.startsWith('Error: ') ? content.slice(7) : content;
            
            contentDiv.innerHTML = `
                <div class="oracle-error">
                    <div class="oracle-error-icon">🔮</div>
                    <div class="oracle-error-message">${cleanError}</div>
                    <div class="oracle-error-hint">This oracle will be available once properly configured.</div>
                </div>
            `;
        } else {
            panel.className = 'oracle-panel complete';
            status.innerHTML = '<i class="fas fa-check"></i> Complete';
            contentDiv.innerHTML = this.formatContent(content, providerKey);
        }
    }
    
    finishComparison() {
        // Add completion animation or effects if needed
        console.log('Comparison complete!');
    }

    showSuccess() {
        const successMsg = document.createElement('div');
        successMsg.className = 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 mt-6 fade-in';
        successMsg.innerHTML = `
            <div class="flex items-center justify-center">
                <span class="text-2xl mr-3">🏆</span>
                <span class="text-green-800 font-semibold">Your legendary quest has been chronicled!</span>
                <span class="text-2xl ml-3">⚔️</span>
            </div>
        `;
        
        this.itineraryContent.appendChild(successMsg);
        
        // Remove success message after 4 seconds
        setTimeout(() => {
            successMsg.remove();
        }, 4000);
    }

    showError(message) {
        const isApiKeyError = message.includes('API key') || message.includes('🔑');
        
        this.comparisonContainer.innerHTML = `
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 2px solid #f59e0b; border-radius: 1rem; padding: 2rem; text-align: center; grid-column: 1 / -1;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">${isApiKeyError ? '🔑' : '⚠️'}</div>
                <h3 style="color: #92400e; font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem;">${message}</h3>
                ${isApiKeyError ? `
                    <div style="background: #e0f2fe; border: 1px solid #0891b2; border-radius: 0.5rem; padding: 1.5rem; margin: 1.5rem 0; text-align: left;">
                        <h4 style="color: #0e7490; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="margin-right: 0.5rem;">ℹ️</span> Setup Instructions:
                        </h4>
                        <ol style="color: #155e75; line-height: 1.6; padding-left: 1rem;">
                            <li>Get API keys from the respective providers</li>
                            <li>Create a <code style="background: #f0f9ff; padding: 0.25rem; border-radius: 0.25rem; font-family: monospace;">.env</code> file</li>
                            <li>Add: <code style="background: #f0f9ff; padding: 0.25rem; border-radius: 0.25rem; font-family: monospace;">OPENAI_API_KEY=your_key</code></li>
                            <li>For Claude: <code style="background: #f0f9ff; padding: 0.25rem; border-radius: 0.25rem; font-family: monospace;">ANTHROPIC_API_KEY=your_key</code></li>
                            <li>For Ollama: Install and run locally</li>
                            <li>Restart the server</li>
                        </ol>
                    </div>
                ` : ''}
                <button onclick="location.reload()" style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; font-weight: 600; padding: 0.75rem 2rem; border: none; border-radius: 0.5rem; margin-top: 1rem; cursor: pointer; transition: all 0.3s ease;" 
                        onmouseover="this.style.background='linear-gradient(135deg, #d97706, #b45309)'" 
                        onmouseout="this.style.background='linear-gradient(135deg, #f59e0b, #d97706)'">
                    🔄 Try Again
                </button>
            </div>
        `;
    }

    switchLanguage(language) {
        console.log('Switching language to:', language);
        if (language === 'dragon') {
            console.log('Applying dragon translations');
            this.applyDragonTranslations();
        } else {
            console.log('Restoring English content');
            this.restoreEnglishContent();
        }
    }

    applyDragonTranslations() {
        if (!window.dragonTranslations) {
            console.log('Dragon translations not available');
            return;
        }
        
        console.log('Applying dragon translations:', window.dragonTranslations);
        const translations = window.dragonTranslations;
        
        // Update header elements
        this.updateElementText('main-title', translations.title);
        this.updateElementText('main-tagline', translations.tagline);
        this.updateElementText('hero-title', translations.hero?.title);
        this.updateElementText('hero-description', translations.hero?.description);
        
        // Update form elements - work with actual HTML structure
        if (translations.form) {
            // Update form header
            const questHeader = document.querySelector('.quest-header h3');
            if (questHeader && translations.form.title) {
                questHeader.textContent = translations.form.title;
            }
            
            const questDesc = document.querySelector('.quest-header p');
            if (questDesc && translations.form.description) {
                questDesc.textContent = translations.form.description;
            }
            
            // Update form labels by finding labels with specific text patterns
            const labels = document.querySelectorAll('label');
            labels.forEach(label => {
                const text = label.textContent.trim();
                if (text.includes('Mystical Realm') && translations.form.fields?.destination?.label) {
                    const icon = label.querySelector('i');
                    label.innerHTML = '';
                    if (icon) label.appendChild(icon);
                    label.appendChild(document.createTextNode(' ' + translations.form.fields.destination.label));
                } else if (text.includes('Quest Duration') && translations.form.fields?.days?.label) {
                    const icon = label.querySelector('i');
                    label.innerHTML = '';
                    if (icon) label.appendChild(icon);
                    label.appendChild(document.createTextNode(' ' + translations.form.fields.days.label));
                } else if (text.includes('Treasury Budget') && translations.form.fields?.budget?.label) {
                    const icon = label.querySelector('i');
                    label.innerHTML = '';
                    if (icon) label.appendChild(icon);
                    label.appendChild(document.createTextNode(' ' + translations.form.fields.budget.label));
                } else if (text.includes('Quest Interests') && translations.form.fields?.interests?.label) {
                    const icon = label.querySelector('i');
                    label.innerHTML = '';
                    if (icon) label.appendChild(icon);
                    label.appendChild(document.createTextNode(' ' + translations.form.fields.interests.label));
                } else if (text.includes('AI Travel Oracles') && translations.form.fields?.providers?.label) {
                    const icon = label.querySelector('i');
                    label.innerHTML = '';
                    if (icon) label.appendChild(icon);
                    label.appendChild(document.createTextNode(' ' + translations.form.fields.providers.label));
                }
            });
            
            // Update submit button
            const submitBtn = document.querySelector('.quest-button');
            if (submitBtn && translations.form.submit_button) {
                submitBtn.textContent = translations.form.submit_button;
            }
            
            // Update placeholder texts
            const destinationSelect = document.getElementById('destination');
            if (destinationSelect && translations.form.fields?.destination?.placeholder) {
                const firstOption = destinationSelect.querySelector('option[value=""]');
                if (firstOption) {
                    firstOption.textContent = translations.form.fields.destination.placeholder;
                }
            }
            
            const budgetSelect = document.getElementById('budget');
            if (budgetSelect && translations.form.fields?.budget?.placeholder) {
                const firstOption = budgetSelect.querySelector('option[value=""]');
                if (firstOption) {
                    firstOption.textContent = translations.form.fields.budget.placeholder;
                }
            }
        }
        
        // Update footer elements if they exist
        if (translations.footer) {
            this.updateElementText('footer-company-name', translations.footer.company_name);
            this.updateElementText('footer-tagline', translations.footer.tagline);
            this.updateElementText('footer-copyright', translations.footer.copyright);
            
            // Update footer links
            if (translations.footer.links) {
                this.updateElementText('footer-about', translations.footer.links.about);
                this.updateElementText('footer-careers', translations.footer.links.careers);
                this.updateElementText('footer-contact', translations.footer.links.contact);
                this.updateElementText('footer-privacy', translations.footer.links.privacy);
                this.updateElementText('footer-terms', translations.footer.links.terms);
            }
            
            // Update social media links
            if (translations.footer.social) {
                this.updateElementText('footer-twitter', translations.footer.social.twitter);
                this.updateElementText('footer-instagram', translations.footer.social.instagram);
                this.updateElementText('footer-facebook', translations.footer.social.facebook);
            }
            
            // Update contact info
            if (translations.footer.contact_info) {
                this.updateElementText('footer-email', translations.footer.contact_info.email);
                this.updateElementText('footer-phone', translations.footer.contact_info.phone);
                this.updateElementText('footer-address', translations.footer.contact_info.address);
            }
        }
    }

    restoreEnglishContent() {
        if (!this.originalContent) return;
        
        // Restore elements by ID
        [
            'main-title', 'main-tagline', 'hero-title', 'hero-description',
            'footer-company-name', 'footer-tagline', 'footer-copyright',
            'footer-about', 'footer-careers', 'footer-contact', 'footer-privacy', 'footer-terms',
            'footer-twitter', 'footer-instagram', 'footer-facebook',
            'footer-email', 'footer-phone', 'footer-address'
        ].forEach(id => {
            if (this.originalContent[id]) {
                this.updateElementText(id, this.originalContent[id]);
            }
        });
        
        // Restore form elements
        if (this.originalContent.questTitle) {
            const questHeader = document.querySelector('.quest-header h3');
            if (questHeader) {
                questHeader.textContent = this.originalContent.questTitle;
            }
        }
        
        if (this.originalContent.questDescription) {
            const questDesc = document.querySelector('.quest-header p');
            if (questDesc) {
                questDesc.textContent = this.originalContent.questDescription;
            }
        }
        
        // Restore original labels
        if (this.originalContent.labels) {
            const labels = document.querySelectorAll('label');
            labels.forEach((label, index) => {
                if (this.originalContent.labels[index]) {
                    label.innerHTML = this.originalContent.labels[index];
                }
            });
        }
        
        // Restore submit button
        if (this.originalContent.submitButton) {
            const submitBtn = document.querySelector('.quest-button');
            if (submitBtn) {
                submitBtn.textContent = this.originalContent.submitButton;
            }
        }
    }

    updateElementText(id, text) {
        const element = document.getElementById(id);
        if (element && text) {
            element.textContent = text;
        }
    }

    initializeLanguageSelector() {
        const languageSelect = document.getElementById('language-select');
        if (!languageSelect) {
            console.log('Language selector not found');
            return;
        }
        console.log('Language selector found, adding event listener');
        
        languageSelect.addEventListener('change', (e) => {
            console.log('Language changed to:', e.target.value);
            this.switchLanguage(e.target.value);
        });
    }

    storeOriginalContent() {
        this.originalContent = {};
        
        // Store main header elements and footer elements
        const elementsById = [
            'main-title', 'main-tagline', 'hero-title', 'hero-description',
            'footer-company-name', 'footer-tagline', 'footer-copyright',
            'footer-about', 'footer-careers', 'footer-contact', 'footer-privacy', 'footer-terms',
            'footer-twitter', 'footer-instagram', 'footer-facebook',
            'footer-email', 'footer-phone', 'footer-address'
        ];
        elementsById.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.originalContent[id] = element.textContent || element.innerHTML;
            }
        });
        
        // Store form elements by selector
        const questHeader = document.querySelector('.quest-header h3');
        if (questHeader) {
            this.originalContent.questTitle = questHeader.textContent;
        }
        
        const questDesc = document.querySelector('.quest-header p');
        if (questDesc) {
            this.originalContent.questDescription = questDesc.textContent;
        }
        
        // Store original label texts
        this.originalContent.labels = {};
        const labels = document.querySelectorAll('label');
        labels.forEach((label, index) => {
            this.originalContent.labels[index] = label.innerHTML;
        });
        
        // Store submit button text
        const submitBtn = document.querySelector('.quest-button');
        if (submitBtn) {
            this.originalContent.submitButton = submitBtn.textContent;
        }
        
        console.log('Stored original content:', this.originalContent);
    }



    async bookItinerary(providerKey, buttonElement) {
        // Find the oracle panel and the itinerary content
        const oraclePanel = buttonElement.closest('.oracle-panel');
        const contentDiv = oraclePanel.querySelector('.oracle-content');
        
        // Clone the content and remove the button to get only the itinerary text
        const itineraryClone = contentDiv.cloneNode(true);
        const buttonToRemove = itineraryClone.querySelector('.book-quest-btn');
        if (buttonToRemove) {
            buttonToRemove.parentElement.remove();
        }
        const itinerary = itineraryClone.innerHTML.trim();

        const allPanels = document.querySelectorAll('.oracle-panel');
        
        // Hide all other panels
        allPanels.forEach(panel => {
            if (panel !== oraclePanel) {
                panel.style.display = 'none';
            }
        });
        
        // Hide the results footer since we'll show confirmation buttons instead
        const resultsFooter = document.querySelector('.results-footer');
        if (resultsFooter) {
            resultsFooter.style.display = 'none';
        }
        
        // Make the confirmed panel take full width
        const comparisonContainer = document.getElementById('comparison-container');
        if (comparisonContainer) {
            comparisonContainer.style.display = 'block';
            comparisonContainer.style.maxWidth = 'none';
        }
        
        // Style the oracle panel to take full width
        oraclePanel.style.width = '100%';
        oraclePanel.style.maxWidth = 'none';
        oraclePanel.style.flex = 'none';
        
        // Get all current form data for booking details
        const destinationSelect = document.getElementById('destination');
        const destination = destinationSelect ? destinationSelect.value : 'mystical realm';
        const daysInput = document.getElementById('days');
        const days = daysInput ? daysInput.value : '7';
        const budgetSelect = document.getElementById('budget');
        const budget = budgetSelect ? budgetSelect.value : 'moderate';
        const interestsChecked = Array.from(document.querySelectorAll('input[name="interests"]:checked')).map(input => input.value);
        
        // Helper function to get mystical display names from form options
        const getDestinationName = (value) => {
            const option = destinationSelect?.querySelector(`option[value="${value}"]`);
            return option ? option.textContent : value;
        };
        
        const getBudgetName = (value) => {
            const option = budgetSelect?.querySelector(`option[value="${value}"]`);
            return option ? option.textContent : value;
        };
        
        const getInterestName = (value) => {
            const checkbox = document.querySelector(`input[name="interests"][value="${value}"]`);
            const label = checkbox?.closest('label');
            return label ? label.textContent.trim() : value;
        };
        
        // Show loading state for oracle response
        oraclePanel.innerHTML = `
            <div class="oracle-header">
                <div class="oracle-title">
                    <i class="fas fa-crystal-ball"></i>
                    <span>Quest Booking...</span>
                </div>
                <div class="oracle-status loading">
                    <i class="fas fa-spinner fa-spin"></i> The Oracle Speaks...
                </div>
            </div>
            <div class="oracle-content">
                <div class="oracle-loading">
                    <div class="oracle-spinner"></div>
                    <p>Your chosen oracle is preparing a final message...</p>
                </div>
            </div>
        `;
        
        let oracleMessage;
        
        try {
            // Get whimsical response from the chosen provider
            console.log('Attempting to fetch booking response for provider:', providerKey);
            const response = await fetch('/generate-booking-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider: providerKey,
                    itinerary: itinerary
                })
            });
            
            console.log('Booking response status:', response.status, response.statusText);
            
            if (!response.ok) {
                // Try to get error message from the server
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { detail: 'Could not parse error response.' };
                }
                console.error('Server returned an error:', errorData);
                throw new Error(`HTTP error! status: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`);
            }
            
            const data = await response.json();
            console.log('Booking response data:', data);
            
            if (data.message && !data.error) {
                oracleMessage = data.message;
                console.log('Using API oracle message');
            } else {
                console.log('API response missing message or has error:', data);
                oracleMessage = "🧙‍♂️ The oracle's final wisdom has been sealed in the mystical void...";
            }
            
        } catch (error) {
            console.error('Error getting oracle response:', error);
            // Fallback oracle message
            oracleMessage = "🌟 The oracle's voice echoes from beyond the mystical veil... Your adventure awaits! ✨";
        }
        
        // Generate the booking confirmation with oracle message
        oraclePanel.innerHTML = `
            <div class="oracle-header">
                <div class="oracle-title">
                    <i class="fas fa-check-circle"></i>
                    <span>Quest Booked!</span>
                </div>
                <div class="oracle-status complete">
                    <i class="fas fa-check-circle"></i> Confirmed
                </div>
            </div>
            <div class="oracle-content">
                <div class="booking-confirmation">
                    <div class="confirmation-header">
                        <h3>✨ Quest Booking Confirmed! ✨</h3>
                        
                        <div class="oracle-final-message">
                            <h4>🔮 Your Oracle's Final Words:</h4>
                            <div class="oracle-wisdom">
                                ${this.formatContent(oracleMessage)}
                            </div>
                        </div>
                    </div>
                    
                    <div class="booking-details">
                        <h4>🗞️ Quest Details:</h4>
                        <div class="quest-details">
                            <div class="detail-item">
                                <strong>🌍 Mystical Realm:</strong> ${getDestinationName(destination)}
                            </div>
                            <div class="detail-item">
                                <strong>⏰ Quest Duration:</strong> ${days} magical days
                            </div>
                            <div class="detail-item">
                                <strong>💰 Treasury Budget:</strong> ${getBudgetName(budget)}
                            </div>
                            ${interestsChecked.length > 0 ? `
                            <div class="detail-item">
                                <strong>⚡ Quest Interests:</strong> ${interestsChecked.map(interest => getInterestName(interest)).join(', ')}
                            </div>
                            ` : ''}
                        </div>
                        
                        <h4>🔮 Magical Booking Process:</h4>
                        <ul class="booking-steps">
                            <li>✅ Quest details transmitted to the Oracle Council</li>
                            <li>✅ Enchanted accommodations being reserved</li>
                            <li>✅ Mystical transportation arranged</li>
                            <li>✅ Ancient billing scrolls prepared</li>
                        </ul>
                        
                        <div class="billing-info">
                            <p><strong>💰 Billing Method:</strong> Enchanted coin transfer via Crystal Communication Network</p>
                            <p><strong>📮 Delivery:</strong> Your quest documents will arrive by magical raven within 24 mystical hours</p>
                            <p><strong>🎫 Confirmation:</strong> Keep this scroll as proof of your booked adventure!</p>
                        </div>
                    </div>
                    
                    <div class="confirmation-actions">
                        <button class="quest-button" onclick="window.print()">
                            📜 Print Quest Confirmation
                        </button>
                        <button class="quest-button secondary" onclick="location.reload()">
                            🗡️ Plan Another Quest
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Update page title
        const resultsTitle = document.querySelector('#results h3');
        if (resultsTitle) {
            resultsTitle.textContent = '🎉 Quest Confirmed!';
        }
        
        // Add celebration effects
        this.addCelebrationEffects();
    }
    
    addCelebrationEffects() {
        // Add extra sparkles for celebration
        const sparkleContainer = document.getElementById('sparkle-container');
        if (sparkleContainer) {
            for (let i = 0; i < 20; i++) {
                setTimeout(() => {
                    const sparkle = document.createElement('div');
                    sparkle.textContent = ['🎉', '✨', '🌟', '🎊', '⭐'][Math.floor(Math.random() * 5)];
                    sparkle.style.position = 'fixed';
                    sparkle.style.left = Math.random() * window.innerWidth + 'px';
                    sparkle.style.top = Math.random() * window.innerHeight + 'px';
                    sparkle.style.fontSize = '2rem';
                    sparkle.style.pointerEvents = 'none';
                    sparkle.style.zIndex = '9999';
                    sparkle.style.animation = 'celebrate 3s ease-out forwards';
                    
                    sparkleContainer.appendChild(sparkle);
                    
                    setTimeout(() => sparkle.remove(), 3000);
                }, i * 100);
            }
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    
    // Initialize the main app
    window.app = new TravelPlannerApp();
    
    // Add some initial animations
    setTimeout(() => {
        const header = document.querySelector('header');
        if (header) {
            header.classList.add('fade-in');
        }
    }, 200);
    
    // Animate the hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.opacity = '0';
        hero.style.transform = 'translateY(30px)';
        setTimeout(() => {
            hero.style.transition = 'all 1s ease-out';
            hero.style.opacity = '1';
            hero.style.transform = 'translateY(0)';
        }, 300);
    }

    // Add floating animation to the compass icon
    const compass = document.querySelector('.fa-compass');
    if (compass) {
        setInterval(() => {
            compass.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                compass.style.transform = 'rotate(0deg)';
            }, 2000);
        }, 10000);
    }

    // Initialize footer link modals
    initializeFooterModals();
    
    console.log('App initialization complete');
});

// Modal functionality for footer links
function initializeFooterModals() {
    // Create modal overlay
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    modalOverlay.innerHTML = `
        <div class="modal-card">
            <div class="modal-header">
                <h3 id="modal-title">Page Title</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-content" id="modal-content">
                Loading...
            </div>
        </div>
    `;
    document.body.appendChild(modalOverlay);

    // Modal content for different pages
    const modalContents = {
        'about': {
            title: 'About Mystical Journeys',
            content: `
                <h4>🏰 Our Mission</h4>
                <p>Mystical Journeys Ltd. is the premier fantasy travel agency specializing in magical realms and extraordinary adventures. Since our founding in the mystical year of 2025, we've been connecting adventurers with their dream quests.</p>
                
                <h4>✨ What We Offer</h4>
                <ul>
                    <li>🐉 Expert AI travel oracles for personalized itineraries</li>
                    <li>🏰 Exclusive access to enchanted realms and kingdoms</li>
                    <li>⚔️ Adventure planning for all experience levels</li>
                    <li>🔮 Magical creature encounters and spell-learning opportunities</li>
                    <li>🏨 Unique accommodations from tree houses to dragon lairs</li>
                </ul>

                <h4>🌟 Our Promise</h4>
                <p>Every quest is crafted to create once-in-a-lifetime experiences that blend adventure, wonder, and personal growth. Our AI oracles work tirelessly to ensure your journey exceeds expectations.</p>
            `
        },
        'contact': {
            title: 'Contact Our Guild',
            content: `
                <h4>📞 Reach Our Travel Oracles</h4>
                <p><strong>Mystical Hotline:</strong> +1 (555) QUEST-ME</p>
                <p><strong>Enchanted Email:</strong> adventures@mystical-journeys.com</p>
                <p><strong>Crystal Chat:</strong> Available 24/7 through our website portal</p>
                
                <h4>🏰 Visit Our Headquarters</h4>
                <p><strong>Address:</strong><br>
                123 Enchanted Way<br>
                Fantasy Realm, FR 12345</p>
                
                <h4>⏰ Oracle Hours</h4>
                <p><strong>Quest Planning:</strong> 24/7 (Our AI oracles never sleep!)<br>
                <strong>Human Support:</strong> Monday-Friday, 9 AM - 6 PM Mystical Time<br>
                <strong>Emergency Adventures:</strong> Available for urgent quest modifications</p>
                
                <h4>🔮 Preferred Contact Methods</h4>
                <ul>
                    <li>Email for detailed quest inquiries</li>
                    <li>Phone for immediate booking assistance</li>
                    <li>Crystal chat for quick questions</li>
                    <li>Raven post for formal correspondence</li>
                </ul>
            `
        },
        'privacy': {
            title: 'Privacy & Magical Data Protection',
            content: `
                <h4>🛡️ Your Quest Data is Sacred</h4>
                <p>At Mystical Journeys, we protect your personal information with the same dedication we use to guard ancient artifacts. Your privacy is paramount to our service.</p>
                
                <h4>🔮 Information We Collect</h4>
                <ul>
                    <li>Quest preferences and travel interests</li>
                    <li>Contact information for booking coordination</li>
                    <li>Adventure feedback to improve our oracles</li>
                    <li>Payment details (encrypted with dragon-grade security)</li>
                </ul>
                
                <h4>✨ How We Use Your Data</h4>
                <ul>
                    <li>Crafting personalized adventure itineraries</li>
                    <li>Sending quest confirmations and updates</li>
                    <li>Improving our AI oracle recommendations</li>
                    <li>Providing customer support and assistance</li>
                </ul>
                
                <h4>🏰 Data Protection</h4>
                <p>Your information is stored in our enchanted vaults, protected by magical barriers and advanced encryption spells. We never share your data with unauthorized third parties or dark wizards.</p>
                
                <p><strong>Last Updated:</strong> October 2025</p>
            `
        },
        'terms': {
            title: 'Terms of Magical Service',
            content: `
                <h4>📜 Quest Agreement</h4>
                <p>By using Mystical Journeys' services, you agree to embark on adventures with courage, respect for magical creatures, and an open mind for wonder.</p>
                
                <h4>⚔️ Adventurer Responsibilities</h4>
                <ul>
                    <li>Treat all magical creatures with respect and kindness</li>
                    <li>Follow realm-specific laws and customs</li>
                    <li>Report any unusual magical phenomena to your guide</li>
                    <li>Maintain your equipment in good condition</li>
                </ul>
                
                <h4>🔮 Service Limitations</h4>
                <ul>
                    <li>AI oracles provide recommendations, not guarantees of specific outcomes</li>
                    <li>Weather spells and magical conditions may affect itineraries</li>
                    <li>Some creatures may be shy and not appear as scheduled</li>
                    <li>Dragon encounters are thrilling but inherently unpredictable</li>
                </ul>
                
                <h4>💰 Billing & Refunds</h4>
                <p>All prices are listed in standard gold coins. Refunds available within 7 mystical days of booking, subject to realm-specific policies.</p>
                
                <h4>⚖️ Dispute Resolution</h4>
                <p>Any disputes will be resolved by the Council of Wise Oracles through magical mediation.</p>
                
                <p><strong>Effective Date:</strong> October 2025</p>
            `
        },
        'careers': {
            title: 'Join Our Magical Team',
            content: `
                <h4>🌟 Work in the World of Wonder</h4>
                <p>Mystical Journeys is always seeking talented individuals to join our quest to create unforgettable adventures. If you're passionate about magic, travel, and helping others discover amazing experiences, we want to hear from you!</p>
                
                <h4>🔮 Open Positions</h4>
                <ul>
                    <li><strong>AI Oracle Trainer:</strong> Help improve our magical recommendation systems</li>
                    <li><strong>Quest Coordinator:</strong> Assist adventurers with booking and travel arrangements</li>
                    <li><strong>Magical Creature Liaison:</strong> Build relationships with dragons, unicorns, and other beings</li>
                    <li><strong>Realm Scout:</strong> Explore new destinations and document experiences</li>
                    <li><strong>Customer Experience Wizard:</strong> Ensure every adventurer has an amazing journey</li>
                </ul>
                
                <h4>✨ What We Offer</h4>
                <ul>
                    <li>Competitive salary in gold coins or your preferred currency</li>
                    <li>Unlimited adventure travel benefits</li>
                    <li>Health coverage including magical healing services</li>
                    <li>Professional development through spell-learning programs</li>
                    <li>Flexible work arrangements (remote crystal ball meetings available)</li>
                </ul>
                
                <h4>📝 How to Apply</h4>
                <p>Send your resume, cover letter, and a short essay about your most magical experience to:</p>
                <p><strong>careers@mystical-journeys.com</strong></p>
                
                <p>Include "Quest for [Position Name]" in the subject line.</p>
            `
        }
    };

    // Add click handlers to footer links
    const footerLinks = document.querySelectorAll('.footer-links a, .social-link');
    footerLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const linkId = link.id.replace('footer-', '');
            
            if (modalContents[linkId]) {
                openModal(modalContents[linkId].title, modalContents[linkId].content);
            } else if (linkId === 'twitter' || linkId === 'instagram' || linkId === 'facebook') {
                openModal('Social Media', `
                    <h4>🌟 Follow Our Adventures</h4>
                    <p>Connect with Mystical Journeys on social media to see amazing quest photos, travel tips, and community stories!</p>
                    <ul>
                        <li><strong>🐦 Twitter:</strong> @MysticalJourneys - Daily adventure inspiration</li>
                        <li><strong>📸 Instagram:</strong> @MysticalJourneysLtd - Stunning realm photography</li>
                        <li><strong>👥 Facebook:</strong> Mystical Journeys Community - Connect with fellow adventurers</li>
                    </ul>
                    <p>Share your quest photos with #MysticalJourneys to be featured!</p>
                `);
            }
        });
    });

    // Close modal when clicking overlay
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
}

function openModal(title, content) {
    const modalOverlay = document.querySelector('.modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    
    modalTitle.textContent = title;
    modalContent.innerHTML = content;
    modalOverlay.classList.add('active');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modalOverlay = document.querySelector('.modal-overlay');
    modalOverlay.classList.remove('active');
    
    // Restore body scroll
    document.body.style.overflow = '';
}