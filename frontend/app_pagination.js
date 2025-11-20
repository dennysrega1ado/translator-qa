// Pagination and New Design Functions

// Function to check if a translation is unreviewed by current user
function isTranslationUnreviewed(translation) {
    // A translation is considered unreviewed if the user hasn't provided
    // scores for coherence, fidelity, and naturalness
    if (!translation.manual_score) {
        return true; // No score at all
    }

    const score = translation.manual_score;
    // Check if all three main scores are missing (null or undefined)
    const hasCoherence = score.coherence !== null && score.coherence !== undefined;
    const hasFidelity = score.fidelity !== null && score.fidelity !== undefined;
    const hasNaturalness = score.naturalness !== null && score.naturalness !== undefined;

    // Return true if any of the three scores is missing
    return !hasCoherence || !hasFidelity || !hasNaturalness;
}

// Get current active filter
function getActiveFilter() {
    const allBtn = document.getElementById('filter-all');
    const unreviewedBtn = document.getElementById('filter-unreviewed');
    const reviewedBtn = document.getElementById('filter-reviewed');

    if (unreviewedBtn && unreviewedBtn.classList.contains('active')) {
        return 'unreviewed';
    } else if (reviewedBtn && reviewedBtn.classList.contains('active')) {
        return 'reviewed';
    }
    return 'all';
}

// Override loadTranslations for pagination
async function loadTranslationsPaginated() {
    console.log('loadTranslationsPaginated called');
    try {
        const loadingEl = document.getElementById('translations-loading');
        const dashboardEl = document.getElementById('translation-dashboard');
        const contentEl = document.getElementById('translation-content');
        const controlsEl = document.getElementById('translation-controls');
        const emptyEl = document.getElementById('translations-empty');

        console.log('Elements found:', { loadingEl, dashboardEl, contentEl, controlsEl, emptyEl });

        if (!loadingEl || !dashboardEl || !contentEl || !controlsEl || !emptyEl) {
            console.error('Required elements not found');
            return;
        }

        // Show dashboard with filters visible, hide content and empty state
        dashboardEl.classList.remove('hidden');
        contentEl.classList.add('hidden');
        controlsEl.classList.add('hidden');
        emptyEl.classList.add('hidden');

        // Show a loading message inside the dashboard (temporarily use empty element)
        emptyEl.innerHTML = '<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div><p class="mt-4 text-slate-600">Loading translations...</p>';
        emptyEl.classList.remove('hidden');

        console.log('Fetching translations...');
        let url = '/translations/?limit=100';

        // Add execution_id filter if selected
        const executionFilter = document.getElementById('execution-filter');
        if (executionFilter && executionFilter.value) {
            url += `&execution_id=${encodeURIComponent(executionFilter.value)}`;
            console.log('Filtering by execution:', executionFilter.value);
        }

        const allTranslations = await apiRequest(url);

        // Apply filter based on active button
        const activeFilter = getActiveFilter();

        if (activeFilter === 'unreviewed') {
            state.translations = allTranslations.filter(t => isTranslationUnreviewed(t));
            console.log('Filtered to unreviewed:', state.translations.length, 'of', allTranslations.length);
        } else if (activeFilter === 'reviewed') {
            state.translations = allTranslations.filter(t => !isTranslationUnreviewed(t));
            console.log('Filtered to reviewed:', state.translations.length, 'of', allTranslations.length);
        } else {
            state.translations = allTranslations;
            console.log('Showing all translations:', state.translations.length);
        }

        state.currentTranslationIndex = 0;

        console.log('Translations loaded:', state.translations.length);

        // Update h1 title with execution description
        const titleElement = document.querySelector('#translation-dashboard h1');

        if (titleElement) {
            if (executionFilter && executionFilter.value) {
                // Get description from the selected option's title attribute
                const selectedOption = executionFilter.options[executionFilter.selectedIndex];
                const description = selectedOption ? selectedOption.getAttribute('title') : null;

                if (description && description !== 'No description') {
                    titleElement.textContent = description;
                } else {
                    titleElement.textContent = 'Translation Review Dashboard';
                }
            } else {
                // No execution selected - showing all executions
                titleElement.textContent = 'Translation Review Dashboard';
            }
        }

        // Hide the loading element
        loadingEl.classList.add('hidden');

        if (state.translations.length === 0) {
            // No translations: hide content and controls, show empty state
            console.log('No translations found');
            contentEl.classList.add('hidden');
            controlsEl.classList.add('hidden');
            // Restore empty state message
            emptyEl.innerHTML = '<span class="material-icons text-slate-300" style="font-size: 64px;">translate</span><p class="mt-4 text-slate-600">No translations available</p>';
            emptyEl.classList.remove('hidden');
        } else {
            // Has translations: show content and controls, hide empty state
            console.log('Rendering translation dashboard');
            contentEl.classList.remove('hidden');
            controlsEl.classList.remove('hidden');
            emptyEl.classList.add('hidden');
            renderCurrentTranslation(true); // Load ratings from DB when loading translations
        }
    } catch (error) {
        console.error('Error loading translations:', error);
        const loadingEl = document.getElementById('translations-loading');
        const dashboardEl = document.getElementById('translation-dashboard');
        const contentEl = document.getElementById('translation-content');
        const controlsEl = document.getElementById('translation-controls');
        const emptyEl = document.getElementById('translations-empty');

        if (loadingEl) loadingEl.classList.add('hidden');
        if (dashboardEl) dashboardEl.classList.remove('hidden');
        if (contentEl) contentEl.classList.add('hidden');
        if (controlsEl) controlsEl.classList.add('hidden');
        if (emptyEl) {
            emptyEl.innerHTML = '<span class="material-icons text-red-300" style="font-size: 64px;">error_outline</span><p class="mt-4 text-slate-600">Error loading translations</p>';
            emptyEl.classList.remove('hidden');
        }
    }
}

function renderCurrentTranslation(loadRatingsFromDB = false) {
    if (state.translations.length === 0) return;

    const translation = state.translations[state.currentTranslationIndex];

    // Note: h1 title is now managed by loadTranslationsPaginated() to show execution description

    // Update pagination info
    document.getElementById('pagination-info').textContent =
        `${state.currentTranslationIndex + 1} of ${state.translations.length}`;

    // Update navigation buttons
    document.getElementById('prev-translation').disabled = state.currentTranslationIndex === 0;
    document.getElementById('next-translation').disabled =
        state.currentTranslationIndex === state.translations.length - 1;

    // Update language display
    document.getElementById('translation-languages').textContent =
        `${translation.source_language.toUpperCase()} → ${translation.target_language.toUpperCase()}`;

    // LLM scores already come in 0-1 scale from S3
    const llmScores = {
        coherence: translation.automated_coherence,
        fidelity: translation.automated_fidelity,
        naturalness: translation.automated_naturalness
    };

    const globalScore = ((llmScores.coherence + llmScores.fidelity + llmScores.naturalness) / 3).toFixed(2);
    document.getElementById('global-llm-score').textContent = globalScore;

    // Extract translation ID with base path from s3 path and display it as subtitle
    let translationId = 'Loading...';
    if (translation && translation.s3_insights_path) {
        // Path format: "llm-output/2025/10/latest/en/52fa10a0f67541a98ce0c2ccba458f9c.json"
        // Remove '/en/' and '.json' to get: "llm-output/2025/10/latest/52fa10a0f67541a98ce0c2ccba458f9c"
        const path = translation.s3_insights_path;
        if (path) {
            // Remove the language folder and extension
            translationId = path.replace('/en/', '/').replace('/es/', '/').replace('.json', '');
        }
    }
    const subtitleEl = document.getElementById('translation-id-subtitle');
    if (subtitleEl) {
        subtitleEl.textContent = translationId;
    }

    // Load existing manual scores from DB only when explicitly requested (e.g., navigating to new translation)
    // This prevents overwriting user's changes while they're rating
    if (loadRatingsFromDB) {
        if (translation.manual_score) {
            state.ratings = {
                coherence: translation.manual_score.coherence || 0,
                fidelity: translation.manual_score.fidelity || 0,
                naturalness: translation.manual_score.naturalness || 0
            };
        } else {
            state.ratings = { coherence: 0, fidelity: 0, naturalness: 0 };
        }
    }

    // If state.ratings doesn't exist yet, initialize it
    if (!state.ratings) {
        if (translation.manual_score) {
            state.ratings = {
                coherence: translation.manual_score.coherence || 0,
                fidelity: translation.manual_score.fidelity || 0,
                naturalness: translation.manual_score.naturalness || 0
            };
        } else {
            state.ratings = { coherence: 0, fidelity: 0, naturalness: 0 };
        }
    }

    // Render metrics cards with current state.ratings
    renderMetricsCards(llmScores, state.ratings);

    // Update text content with line breaks
    document.getElementById('original-text').innerHTML = translation.original_content.replace(/\n/g, '<br>');
    document.getElementById('translated-text').innerHTML = translation.translated_content.replace(/\n/g, '<br>');

    // Populate notes textarea with existing notes if available
    const notesTextarea = document.getElementById('review-notes');
    if (notesTextarea) {
        notesTextarea.value = translation.manual_score?.notes || '';
    }
}

function renderMetricsCards(llmScores, manualScore) {
    const metricsGrid = document.getElementById('metrics-grid');

    const metrics = [
        { title: 'Coherence', llmScore: llmScores.coherence, userScore: manualScore?.coherence || 0, icon: 'description' },
        { title: 'Fidelity', llmScore: llmScores.fidelity, userScore: manualScore?.fidelity || 0, icon: 'check_circle' },
        { title: 'Naturalness', llmScore: llmScores.naturalness, userScore: manualScore?.naturalness || 0, icon: 'thumb_up' }
    ];

    metricsGrid.innerHTML = metrics.map(metric => renderMetricCard(metric)).join('');

    // Attach event listeners to star buttons
    metrics.forEach(metric => {
        const aspect = metric.title.toLowerCase();
        for (let star = 1; star <= 5; star++) {
            const btn = document.getElementById(`star-${aspect}-${star}`);
            if (btn) {
                btn.addEventListener('click', () => handleRating(aspect, star));
            }
        }

        // Attach hover event listeners for info tooltips
        const infoIcon = document.getElementById(`info-icon-${aspect}`);
        const tooltip = document.getElementById(`tooltip-${aspect}`);
        if (infoIcon && tooltip) {
            infoIcon.addEventListener('mouseenter', () => {
                tooltip.classList.remove('hidden');
            });
            infoIcon.addEventListener('mouseleave', () => {
                tooltip.classList.add('hidden');
            });
        }
    });
}

function renderMetricCard({ title, llmScore, userScore, icon }) {
    const percentage = llmScore * 100;
    let colorClass = "from-red-500 to-red-600";
    if (llmScore >= 0.7) colorClass = "from-green-500 to-green-600";
    else if (llmScore >= 0.5) colorClass = "from-yellow-500 to-yellow-600";

    const aspectInfo = {
        coherence: "Evaluates whether the translation maintains the logical structure and connection between ideas from the original text.",
        fidelity: "Measures how faithfully the exact meaning of the original text has been transferred without omissions or additions.",
        naturalness: "Determines if the translated text sounds fluid and natural in the target language, as if it had been originally written in that language."
    };

    return `
        <div class="bg-white rounded-xl shadow-md p-6 border border-slate-200">
            <div class="flex items-center gap-3 mb-4">
                <div class="p-2 rounded-lg bg-gradient-to-br ${colorClass}">
                    <span class="material-icons text-white">${icon}</span>
                </div>
                <h3 class="font-semibold text-slate-700">${title}</h3>
                <div class="relative ml-auto">
                    <span id="info-icon-${title.toLowerCase()}" class="material-icons text-slate-400 cursor-help text-lg">info</span>
                    <div id="tooltip-${title.toLowerCase()}" class="hidden absolute right-0 top-8 z-50 w-72 bg-slate-800 text-white text-xs p-3 rounded-lg shadow-xl">
                        ${aspectInfo[title.toLowerCase()]}
                    </div>
                </div>
            </div>

            <div class="space-y-4">
                <!-- LLM Reference Score -->
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-medium text-slate-500 uppercase tracking-wide">LLM Reference</span>
                        <span class="text-2xl font-bold text-slate-700">${llmScore.toFixed(2)}</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div class="h-full bg-gradient-to-r ${colorClass} transition-all duration-300" style="width: ${percentage}%"></div>
                    </div>
                </div>

                <!-- User Rating -->
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-medium text-blue-600 uppercase tracking-wide">Your Rating</span>
                        <span class="text-sm font-semibold text-blue-600">${userScore > 0 ? `${userScore.toFixed(2)}` : 'Not rated'}</span>
                    </div>
                    <div class="flex gap-1">
                        ${renderStarRating(title.toLowerCase(), Math.round(userScore * 5))}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderStarRating(aspect, value) {
    return [1, 2, 3, 4, 5].map(star => `
        <button id="star-${aspect}-${star}" class="focus:outline-none transition-transform hover:scale-110">
            <span class="material-icons ${star <= value ? 'text-yellow-400' : 'text-gray-300'}" style="font-size: 20px;">
                ${star <= value ? 'star' : 'star_border'}
            </span>
        </button>
    `).join('');
}

function handleRating(aspect, star) {
    // Convert 1-5 stars to 0-1 scale
    // 1 star = 0.2, 2 stars = 0.4, 3 stars = 0.6, 4 stars = 0.8, 5 stars = 1.0
    const score = star * 0.2;
    state.ratings[aspect] = score;
    renderCurrentTranslation();
}

function navigateTranslation(direction) {
    const newIndex = state.currentTranslationIndex + direction;
    if (newIndex >= 0 && newIndex < state.translations.length) {
        state.currentTranslationIndex = newIndex;
        // Load ratings from DB when navigating to a new translation
        renderCurrentTranslation(true);
    }
}

async function submitCurrentReview() {
    const translation = state.translations[state.currentTranslationIndex];

    // Get the notes from the textarea
    const notesTextarea = document.getElementById('review-notes');
    const notes = notesTextarea ? notesTextarea.value.trim() : '';

    const scoreData = {
        coherence: state.ratings.coherence || null,
        fidelity: state.ratings.fidelity || null,
        naturalness: state.ratings.naturalness || null,
        overall: state.ratings.coherence && state.ratings.fidelity && state.ratings.naturalness
            ? ((state.ratings.coherence + state.ratings.fidelity + state.ratings.naturalness) / 3)
            : null,
        notes: notes || null
    };

    try {
        if (translation.manual_score) {
            // Update existing score
            await apiRequest(`/scores/${translation.manual_score.id}`, {
                method: 'PUT',
                body: JSON.stringify(scoreData)
            });
        } else {
            // Create new score
            await apiRequest('/scores/', {
                method: 'POST',
                body: JSON.stringify({
                    translation_id: translation.id,
                    ...scoreData
                })
            });
        }

        // Show success animation
        showSuccessAnimation();

        // Wait for animation to finish
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Reload translations to update scores
        await loadTranslationsPaginated();

        // Find next unreviewed translation
        const nextUnreviewedIndex = findNextUnreviewed();

        if (nextUnreviewedIndex !== -1) {
            // Navigate to next unreviewed
            state.currentTranslationIndex = nextUnreviewedIndex;
            renderCurrentTranslation(true);
        } else {
            // No more unreviewed, check if filter is active
            const activeFilter = getActiveFilter();
            if (activeFilter === 'unreviewed') {
                // Show completion modal
                showAllDoneModal();
            }
        }
    } catch (error) {
        alert(`Error submitting review: ${error.message}`);
    }
}

function showSuccessAnimation() {
    const overlay = document.getElementById('success-overlay');
    overlay.classList.remove('hidden');

    setTimeout(() => {
        overlay.classList.add('hidden');
    }, 1000);
}

function findNextUnreviewed() {
    // Start searching from the next translation
    for (let i = state.currentTranslationIndex + 1; i < state.translations.length; i++) {
        if (isTranslationUnreviewed(state.translations[i])) {
            return i;
        }
    }

    // If not found ahead, search from the beginning
    for (let i = 0; i < state.currentTranslationIndex; i++) {
        if (isTranslationUnreviewed(state.translations[i])) {
            return i;
        }
    }

    return -1; // No unreviewed translations found
}

function showAllDoneModal() {
    const modal = document.getElementById('all-done-modal');
    modal.classList.remove('hidden');
}

function searchTranslationById() {
    const searchInput = document.getElementById('search-translation-id');
    const searchId = searchInput.value.trim();

    if (!searchId) {
        alert('Please enter a translation ID to search');
        return;
    }

    // Search for translation by ID in s3_insights_path
    const foundIndex = state.translations.findIndex(t => {
        if (!t.s3_insights_path) return false;

        // Extract the ID from the s3_insights_path
        // Path format: "llm-output/2025/10/latest/en/52fa10a0f67541a98ce0c2ccba458f9c.json"
        // We want to extract: "52fa10a0f67541a98ce0c2ccba458f9c"
        const pathParts = t.s3_insights_path.split('/');
        const filename = pathParts[pathParts.length - 1]; // Get last part (filename)
        const translationId = filename.replace('.json', ''); // Remove extension

        // Check if the ID contains the search term
        return translationId.includes(searchId);
    });

    if (foundIndex !== -1) {
        state.currentTranslationIndex = foundIndex;
        renderCurrentTranslation(true); // Load ratings from DB when searching
        searchInput.value = ''; // Clear search input
    } else {
        alert(`Translation with ID "${searchId}" not found`);
    }
}

// Execution filter functions
async function loadExecutions() {
    try {
        const executions = await apiRequest('/translations/executions/list');
        renderExecutionFilter(executions);
    } catch (error) {
        console.error('Error loading executions:', error);
        const executionFilter = document.getElementById('execution-filter');
        if (executionFilter) {
            executionFilter.innerHTML = '<option value="">Error loading executions</option>';
        }
    }
}

function renderExecutionFilter(executions) {
    const executionFilter = document.getElementById('execution-filter');
    if (!executionFilter) return;

    if (executions.length === 0) {
        executionFilter.innerHTML = '<option value="">No executions available</option>';
        return;
    }

    // Build options HTML - start with "All Executions"
    let html = '<option value="">All Executions</option>';

    executions.forEach((exec) => {
        const date = exec.latest_date ? new Date(exec.latest_date).toLocaleString() : 'Unknown date';
        const description = exec.description || 'No description';
        const label = `${exec.execution_id} (${exec.count} translations) - ${date}`;
        html += `<option value="${exec.execution_id}" title="${description}">${label}</option>`;
    });

    executionFilter.innerHTML = html;
}

function handleExecutionFilterChange() {
    // Automatically reload translations when execution filter changes
    loadTranslationsPaginated();
}
