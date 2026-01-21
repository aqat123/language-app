// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global State
let currentUser = {
    id: '',
    language: '',
    level: ''
};
let currentFlashcard = null;
let currentConversationId = null;
let currentGrammarQuestion = null;

// Utility Functions
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function showError(message) {
    alert('Error: ' + message);
}

// User Registration
async function registerUser() {
    const userId = document.getElementById('user-id').value.trim();
    const language = document.getElementById('language').value;
    const level = document.getElementById('level').value;

    if (!userId) {
        showError('Please enter your name');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                external_id: userId,
                target_language: language,
                level: level
            })
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = {
                id: userId,
                language: language,
                level: level
            };

            document.getElementById('user-display').textContent =
                `${userId} | ${language} (${level})`;
            document.getElementById('user-info').classList.remove('hidden');

            showSection('module-section');
        } else if (response.status === 400) {
            currentUser = {
                id: userId,
                language: language,
                level: level
            };
            document.getElementById('user-display').textContent =
                `${userId} | ${language} (${level})`;
            document.getElementById('user-info').classList.remove('hidden');
            showSection('module-section');
        } else {
            throw new Error('Failed to register user');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Module Navigation
function backToModules() {
    showSection('module-section');
}

// Vocabulary Module
async function startVocabulary() {
    showSection('vocabulary-section');
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading flashcard...</div>';
    document.getElementById('options-container').classList.add('hidden');
    document.getElementById('feedback').classList.add('hidden');

    try {
        const response = await fetch(
            `${API_BASE_URL}/vocabulary/next?user_id=${currentUser.id}&target_language=${currentUser.language}&level=${currentUser.level}`
        );

        if (!response.ok) throw new Error('Failed to load flashcard');

        currentFlashcard = await response.json();
        displayFlashcard();
    } catch (error) {
        document.getElementById('flashcard').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displayFlashcard() {
    const flashcardHtml = `
        <div class="word">${currentFlashcard.word}</div>
        <div class="example">"${currentFlashcard.example_sentence}"</div>
        <div class="definition-label">What does this mean?</div>
    `;
    document.getElementById('flashcard').innerHTML = flashcardHtml;

    const optionsHtml = currentFlashcard.options.map((option, index) => `
        <div class="option" onclick="selectOption(${index})">
            ${option}
        </div>
    `).join('');

    document.getElementById('options-container').innerHTML = optionsHtml;
    document.getElementById('options-container').classList.remove('hidden');
}

async function selectOption(selectedIndex) {
    const options = document.querySelectorAll('.option');
    const correctIndex = currentFlashcard.correct_option_index;

    options.forEach(opt => opt.style.pointerEvents = 'none');

    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    }

    try {
        const response = await fetch(`${API_BASE_URL}/vocabulary/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                word: currentFlashcard.word,
                selected_option_index: selectedIndex,
                correct_option_index: correctIndex
            })
        });

        const result = await response.json();

        const feedbackDiv = document.getElementById('feedback');
        const isCorrect = result.is_correct;
        feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
        feedbackDiv.innerHTML = `
            <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
            <div class="feedback-explanation">${result.explanation}</div>
            <button onclick="startVocabulary()" class="btn btn-primary" style="margin-top: 15px;">Next Word</button>
        `;
        feedbackDiv.classList.remove('hidden');
    } catch (error) {
        showError(error.message);
    }
}

// Conversation Module
async function startConversation() {
    showSection('conversation-section');
    document.getElementById('chat-container').innerHTML = '<div class="loading">Starting conversation...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/conversation/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                target_language: currentUser.language,
                level: currentUser.level
            })
        });

        if (!response.ok) throw new Error('Failed to start conversation');

        const data = await response.json();
        currentConversationId = data.session_id;

        document.getElementById('chat-container').innerHTML = `
            <div class="chat-message ai">${data.opening_message}</div>
        `;
    } catch (error) {
        document.getElementById('chat-container').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML += `<div class="chat-message user">${message}</div>`;
    input.value = '';

    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch(
            `${API_BASE_URL}/conversation/${currentConversationId}/message`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: currentUser.id,
                    message: message
                })
            }
        );

        if (!response.ok) throw new Error('Failed to send message');

        const data = await response.json();

        chatContainer.innerHTML += `<div class="chat-message ai">${data.reply}</div>`;

        if (data.corrected_user_message && data.corrected_user_message !== message) {
            chatContainer.innerHTML += `
                <div class="chat-message ai" style="background: #fff3e0; font-size: 0.9rem;">
                    💡 Correction: "${data.corrected_user_message}"
                </div>
            `;
        }

        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        showError(error.message);
    }
}

// Grammar Module
async function startGrammar() {
    showSection('grammar-section');
    document.getElementById('grammar-question').innerHTML = '<div class="loading">Loading question...</div>';
    document.getElementById('grammar-options').classList.add('hidden');
    document.getElementById('grammar-feedback').classList.add('hidden');

    try {
        const response = await fetch(
            `${API_BASE_URL}/grammar/question?user_id=${currentUser.id}&target_language=${currentUser.language}&level=${currentUser.level}&topic=general`
        );

        if (!response.ok) throw new Error('Failed to load grammar question');

        currentGrammarQuestion = await response.json();
        displayGrammarQuestion();
    } catch (error) {
        document.getElementById('grammar-question').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displayGrammarQuestion() {
    document.getElementById('grammar-question').innerHTML = `
        <div style="font-size: 1.5rem; margin-bottom: 20px;">${currentGrammarQuestion.question_text}</div>
    `;

    const optionsHtml = currentGrammarQuestion.options.map((option, index) => `
        <div class="option" onclick="selectGrammarOption(${index})">
            ${option}
        </div>
    `).join('');

    document.getElementById('grammar-options').innerHTML = optionsHtml;
    document.getElementById('grammar-options').classList.remove('hidden');
}

async function selectGrammarOption(selectedIndex) {
    const options = document.querySelectorAll('#grammar-options .option');
    const correctIndex = currentGrammarQuestion.correct_option_index;

    options.forEach(opt => opt.style.pointerEvents = 'none');

    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    }

    const feedbackDiv = document.getElementById('grammar-feedback');
    const isCorrect = selectedIndex === correctIndex;
    feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
    feedbackDiv.innerHTML = `
        <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
        <div class="feedback-explanation">${currentGrammarQuestion.explanation}</div>
        <button onclick="startGrammar()" class="btn btn-primary" style="margin-top: 15px;">Next Question</button>
    `;
    feedbackDiv.classList.remove('hidden');
}

// Writing Module
function startWriting() {
    showSection('writing-section');
    document.getElementById('writing-language').textContent = currentUser.language;
    document.getElementById('writing-text').value = '';
    document.getElementById('writing-feedback').classList.add('hidden');
}

async function submitWriting() {
    const text = document.getElementById('writing-text').value.trim();

    if (!text) {
        showError('Please write something first');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/writing/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                target_language: currentUser.language,
                level: currentUser.level,
                text: text
            })
        });

        if (!response.ok) throw new Error('Failed to get feedback');

        const data = await response.json();

        const feedbackDiv = document.getElementById('writing-feedback');
        feedbackDiv.innerHTML = `
            <div class="corrected-text">
                <h3>✅ Corrected Text:</h3>
                <p style="font-size: 1.2rem; margin-top: 10px;">${data.corrected_text}</p>
            </div>
            <div class="feedback-comment">
                <h3>💬 Feedback:</h3>
                <p style="margin-top: 10px;">${data.overall_comment}</p>
                ${data.inline_explanation ? `<p style="margin-top: 10px; font-size: 0.9rem; color: #666;">${data.inline_explanation}</p>` : ''}
            </div>
            ${data.score ? `<div class="score">Score: ${data.score}%</div>` : ''}
            <button onclick="startWriting()" class="btn btn-primary">Try Another</button>
        `;
        feedbackDiv.classList.remove('hidden');
    } catch (error) {
        showError(error.message);
    }
}

// Progress
async function showProgress() {
    showSection('progress-section');
    document.getElementById('progress-container').innerHTML = '<div class="loading">Loading progress...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser.id}/progress`);

        if (!response.ok) throw new Error('Failed to load progress');

        const progressData = await response.json();

        if (progressData.length === 0) {
            document.getElementById('progress-container').innerHTML =
                '<p style="text-align: center; color: #666; padding: 40px;">No progress yet. Start practicing!</p>';
            return;
        }

        const progressHtml = progressData.map(item => `
            <div class="progress-item">
                <h3>${item.module.charAt(0).toUpperCase() + item.module.slice(1)}</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${item.score || 0}%">
                        ${Math.round(item.score || 0)}%
                    </div>
                </div>
                <p style="margin-top: 10px; color: #666;">
                    ${item.correct_attempts} out of ${item.total_attempts} correct
                </p>
            </div>
        `).join('');

        document.getElementById('progress-container').innerHTML = progressHtml;
    } catch (error) {
        document.getElementById('progress-container').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}
