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
let currentTargetPhrase = "";
let mediaRecorder = null;
let audioChunks = [];
let audioBlob = null;
let nextFlashcardPromise = null;

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

        // see if you can preload the next flashcard
        preloadNextFlashcard();

    } catch (error) {
        document.getElementById('flashcard').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displayFlashcard() {
    let imageHtml = '';
    if (currentFlashcard.image_data) {
        imageHtml = `
            <div class="flashcard-image" style="margin-top: 20px; text-align: center;">
                <img 
                    src="data:image/jpeg;base64,${currentFlashcard.image_data}" 
                    alt="${currentFlashcard.word}" 
                    style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                >
            </div>
        `;
    }

    const flashcardHtml = `
        <div class="word">${currentFlashcard.word}</div>
        <div class="example">"${currentFlashcard.example_sentence}"</div>
        <div class="definition-label">What does this mean?</div>
        ${imageHtml}
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

function preloadNextFlashcard() {
    // Start the fetch request immediately and store the word
    nextFlashcardPromise = fetch(
        `${API_BASE_URL}/vocabulary/next?user_id=${currentUser.id}&target_language=${currentUser.language}&level=${currentUser.level}`
    )
    .then(response => {
        if (!response.ok) throw new Error('Failed to load flashcard');
        return response.json();
    })
    .catch(error => {
        console.error("Preload error:", error);
        return null;
    });
}

async function loadNextWord() {
    // Reset UI state
    document.getElementById('options-container').classList.add('hidden');
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading next word...</div>';

    try {
        let nextCardData = null;

        // Check if we have a pre-loaded word
        if (nextFlashcardPromise) {
            // Wait for the pre-load to finish
            nextCardData = await nextFlashcardPromise;
        }

        // If pre-load failed or didn't exist, fetch normally
        if (!nextCardData) {
            const response = await fetch(
                `${API_BASE_URL}/vocabulary/next?user_id=${currentUser.id}&target_language=${currentUser.language}&level=${currentUser.level}`
            );
            nextCardData = await response.json();
        }

        // Swap Data
        currentFlashcard = nextCardData;
        displayFlashcard();

        // Trigger the next pre-fetch too for max efficiency
        preloadNextFlashcard();

    } catch (error) {
        document.getElementById('flashcard').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function selectOption(selectedIndex) {
    const options = document.querySelectorAll('.option');
    const correctIndex = currentFlashcard.correct_option_index;

    options.forEach(opt => opt.style.pointerEvents = 'none');

    // allow correctness check immediately
    const isCorrect = (selectedIndex === correctIndex);

    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    }

    // Show the Feedback placeholder before the api call
    const feedbackDiv = document.getElementById('feedback');
    feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
    feedbackDiv.innerHTML = `
        <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
        <div class="feedback-explanation">
            <em>Loading explanation...</em>
        </div>
        <button onclick="loadNextWord()" class="btn btn-primary" style="margin-top: 15px;">Next Word</button>
    `;
    feedbackDiv.classList.remove('hidden');

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

        // fill feedback explanation now
        const explanationEl = feedbackDiv.querySelector('.feedback-explanation');
        if (explanationEl) {
            explanationEl.innerHTML = result.explanation;
        }

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

        // start of change
        const hasCorrection = data.corrected_user_message && data.corrected_user_message !== message && data.corrected_user_message !== "null";
        const hasTips = data.tips && data.tips !== "null";

        if (hasCorrection || hasTips) {
            let feedbackHtml = `
                <div class="chat-message ai" style="background: #fff3e0; font-size: 0.9rem; border-left: 4px solid #ffca28; color: #5d4037;">
            `;

            if (hasCorrection) {
                feedbackHtml += `<div style="margin-bottom: 6px;"><strong>💡 Correction:</strong> "${data.corrected_user_message}"</div>`;
            }

            if (hasTips) {
                feedbackHtml += `<div style="font-style: italic; font-size: 0.85rem; color: #795548;">👉 ${data.tips}</div>`;
            }

            feedbackHtml += `</div>`;
            chatContainer.innerHTML += feedbackHtml;
        }
        // end of change

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

// Phonetics Module
async function startPhonetics() {
    showSection('phonetics-section');

    // Reset UI
    document.getElementById('target-phrase').innerHTML = '<div class="loading">Generating phrase...</div>';
    document.getElementById('phonetics-feedback').classList.add('hidden');
    document.getElementById('validate-btn').disabled = true;
    document.getElementById('audio-preview').style.display = 'none';
    document.getElementById('record-status').textContent = "Tap to Record";
    document.getElementById('record-btn').style.backgroundColor = "#e74c3c"; // Red
    document.getElementById('record-btn').innerHTML = "🎙️";

    // Reset Audio State
    audioBlob = null;
    audioChunks = [];

    try {
        // Fetch new phrase from Backend
        const response = await fetch(
            `${API_BASE_URL}/phonetics/phrase?target_language=${currentUser.language}&level=${currentUser.level}`
        );

        if (!response.ok) throw new Error('Failed to load phrase');

        const data = await response.json();
        currentTargetPhrase = data.target_phrase;

        document.getElementById('target-phrase').textContent = currentTargetPhrase;

    } catch (error) {
        document.getElementById('target-phrase').innerHTML = `<div style="color:red">Error: ${error.message}</div>`;
    }
}

// Recording Audio
async function toggleRecording() {
    const recordBtn = document.getElementById('record-btn');
    const statusText = document.getElementById('record-status');

    // If already recording, STOP it
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.style.backgroundColor = "#e74c3c"; // Back to Red
        recordBtn.innerHTML = "🎙️";
        statusText.textContent = "Recording saved. Ready to validate.";
        return;
    }

    // START Recording
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            // Create Blob when stopped
            audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

            // Enable Validate Button
            document.getElementById('validate-btn').disabled = false;

            // Show Preview Player
            const audioUrl = URL.createObjectURL(audioBlob);
            const audioPreview = document.getElementById('audio-preview');
            audioPreview.src = audioUrl;
            audioPreview.style.display = 'block';
        };

        mediaRecorder.start();
        recordBtn.style.backgroundColor = "#f1c40f"; // Yellow/Orange for active recording
        recordBtn.innerHTML = "⏹️"; // Stop icon
        statusText.textContent = "Recording... Tap to stop";

    } catch (err) {
        showError("Microphone access denied: " + err.message);
    }
}

// Validate Pronunciation
async function validatePronunciation() {
    if (!audioBlob) {
        showError("Please record something first!");
        return;
    }

    const validateBtn = document.getElementById('validate-btn');
    validateBtn.disabled = true;
    validateBtn.textContent = "Analyzing...";

    // Prepare Form Data
    const formData = new FormData();
    formData.append("user_id", currentUser.id);
    formData.append("target_language", currentUser.language);
    formData.append("target_phrase", currentTargetPhrase);
    // Send file with correct extension
    formData.append("audio_file", audioBlob, "recording.webm");

    try {
        const response = await fetch(`${API_BASE_URL}/phonetics/evaluate`, {
            method: 'POST',
            body: formData // No Content-Type header needed (browser sets it for FormData)
        });

        if (!response.ok) throw new Error('Analysis failed');

        const result = await response.json();
        displayPhoneticsFeedback(result);

    } catch (error) {
        showError(error.message);
    } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = "Validate Pronunciation";
    }
}

// Display the feedback
function displayPhoneticsFeedback(result) {
    const feedbackContainer = document.getElementById('phonetics-feedback');
    const mainFeedback = document.getElementById('phonetics-main-feedback');
    const wordFeedback = document.getElementById('phonetics-word-feedback');

    // 1. Main Feedback (Score & General)
    const isGood = result.score > 70;
    mainFeedback.className = 'feedback ' + (isGood ? 'correct' : 'incorrect');
    mainFeedback.innerHTML = `
        <div class="feedback-text">Score: ${result.score}/100</div>
        <div class="feedback-explanation">
            <strong>Heard:</strong> "${result.transcript}"<br><br>
            ${result.feedback}
        </div>
    `;

    // 2. Word-Level Feedback (Yellow Bubbles)
    let wordHtml = '';
    if (result.word_level_feedback && result.word_level_feedback.length > 0) {
        wordHtml += `<div style="margin-top: 15px; font-weight: bold; color: #555;">Specific Issues:</div>`;

        result.word_level_feedback.forEach(issue => {
            wordHtml += `
                <div style="background: #fff3e0; border-left: 4px solid #ffca28; padding: 10px; margin-top: 10px; border-radius: 4px; color: #5d4037;">
                    <div><strong>Word:</strong> "${issue.word}"</div>
                    <div><strong>Issue:</strong> ${issue.issue}</div>
                    <div style="font-style: italic; font-size: 0.9rem; margin-top: 4px;">👉 Tip: ${issue.tip}</div>
                </div>
            `;
        });
    } else if (result.score < 100) {
         wordHtml = `<div style="margin-top: 10px; color: #666; font-style: italic;">No specific word errors detected. Work on overall flow!</div>`;
    }

    wordFeedback.innerHTML = wordHtml;
    feedbackContainer.classList.remove('hidden');
}