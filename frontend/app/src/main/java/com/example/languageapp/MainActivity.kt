package com.example.languageapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // Force white background for consistency
            Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
                AppNavigation()
            }
        }
    }
}

// NETWORK CLIENT
object RetrofitClient {
    // 10.0.2.2 is the Android Emulator's alias for "localhost"
    private const val BASE_URL = "http://10.0.2.2:8000"

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

// NAVIGATION HOST
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "dashboard") {
        composable("dashboard") { DashboardScreen(navController) }
        composable("quiz") { QuizScreen(navController) }
        composable("chat") { ChatScreen(navController) }
        composable("vocab") { VocabScreen(navController) }
    }
}

// DASHBOARD
@Composable
fun DashboardScreen(navController: NavController) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Language App AI", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(48.dp))

        MenuButton("Start Quiz (Pronunciation)") { navController.navigate("quiz") }
        Spacer(Modifier.height(16.dp))
        MenuButton("Start Chat (Conversation)") { navController.navigate("chat") }
        Spacer(Modifier.height(16.dp))
        MenuButton("Vocab Learning (Flashcards)") { navController.navigate("vocab") }
    }
}

@Composable
fun MenuButton(text: String, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().height(56.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(text, fontSize = 18.sp)
    }
}

// QUIZ SCREEN (PRONUNCIATION)
@Composable
fun QuizScreen(navController: NavController) {
    var feedback by remember { mutableStateOf("Press 'Record' and read the phrase.") }
    var score by remember { mutableStateOf("") }
    var isProcessing by remember { mutableStateOf(false) }

    // Hardcoded for now, but could come from Backend later
    val targetPhrase = "Through the door"

    ScreenTemplate(title = "Pronunciation Quiz", navController = navController) {
        // The "Text Rectangle" Challenge
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            Column(Modifier.padding(24.dp)) {
                Text("Read this aloud:", style = MaterialTheme.typography.labelLarge)
                Spacer(Modifier.height(8.dp))
                Text(targetPhrase, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(Modifier.height(32.dp))

        // Simulated Record Button
        Button(
            onClick = {
                isProcessing = true
                feedback = "Analyzing..."
                // MOCKING AUDIO UPLOAD: We just send the text to check connection
                val req = PhoneticsRequest(language = "English", targetPhrase = targetPhrase)
                RetrofitClient.apiService.checkPronunciation(req).enqueue(object : Callback<PhoneticsResponse> {
                    override fun onResponse(call: Call<PhoneticsResponse>, response: Response<PhoneticsResponse>) {
                        isProcessing = false
                        if (response.isSuccessful) {
                            val body = response.body()
                            score = "Score: ${(body?.score ?: 0.0) * 100}%"
                            feedback = body?.feedback?.joinToString("\n") ?: "Good job!"
                        } else {
                            feedback = "Error: ${response.code()}"
                        }
                    }
                    override fun onFailure(call: Call<PhoneticsResponse>, t: Throwable) {
                        isProcessing = false
                        feedback = "Connection failed: ${t.localizedMessage}"
                    }
                })
            },
            enabled = !isProcessing,
            modifier = Modifier.size(120.dp),
            shape = RoundedCornerShape(60.dp), // Circle
            colors = ButtonDefaults.buttonColors(containerColor = Color.Red)
        ) {
            Text(if (isProcessing) "..." else "🎤", fontSize = 40.sp)
        }

        Spacer(Modifier.height(24.dp))
        Text(score, style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(8.dp))
        Text(feedback, textAlign = TextAlign.Center)
    }
}

// CHAT SCREEN
@Composable
fun ChatScreen(navController: NavController) {
    var messageText by remember { mutableStateOf("") }
    // UI History (Bubbles)
    var chatHistory by remember { mutableStateOf(listOf<Pair<String, Boolean>>()) }
    // Backend Context (List of Strings for Python)
    var backendContext by remember { mutableStateOf(listOf<String>()) }
    var isSending by remember { mutableStateOf(false) }

    ScreenTemplate(title = "AI Chat Tutor", navController = navController) {
        // Chat History List
        LazyColumn(
            modifier = Modifier.weight(1f).fillMaxWidth().padding(8.dp),
            reverseLayout = true // Show newest at bottom (if we inverted list, but simplistic here)
        ) {
            items(chatHistory) { (msg, isUser) ->
                ChatBubble(text = msg, isUser = isUser)
            }
        }

        // Input Area
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = messageText,
                onValueChange = { messageText = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Type in Spanish...") }
            )
            Spacer(Modifier.width(8.dp))
            Button(
                enabled = messageText.isNotBlank() && !isSending,
                onClick = {
                    val userMsg = messageText
                    messageText = "" // clear input
                    chatHistory = chatHistory + (userMsg to true)
                    isSending = true

                    val req = ChatRequest(language = "Spanish", user_msg = userMsg, context = backendContext)

                    RetrofitClient.apiService.sendMessage(req).enqueue(object : Callback<ChatResponse> {
                        override fun onResponse(call: Call<ChatResponse>, response: Response<ChatResponse>) {
                            isSending = false
                            if (response.isSuccessful) {
                                val body = response.body()
                                val reply = body?.reply ?: "..."
                                // UPDATE CONTEXT FROM SERVER
                                backendContext = body?.context ?: emptyList()
                                chatHistory = chatHistory + (reply to false)
                            } else {
                                chatHistory = chatHistory + ("Error: ${response.code()}" to false)
                            }
                        }
                        override fun onFailure(call: Call<ChatResponse>, t: Throwable) {
                            isSending = false
                            chatHistory = chatHistory + ("Failed: ${t.localizedMessage}" to false)
                        }
                    })
                }
            ) {
                Text("Send")
            }
        }
    }
}

@Composable
fun ChatBubble(text: String, isUser: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        Surface(
            color = if (isUser) MaterialTheme.colorScheme.primary else Color.LightGray,
            shape = RoundedCornerShape(16.dp),
            modifier = Modifier.padding(4.dp).widthIn(max = 250.dp)
        ) {
            Text(
                text = text,
                color = if (isUser) Color.White else Color.Black,
                modifier = Modifier.padding(12.dp)
            )
        }
    }
}

@Composable
fun VocabScreen(navController: NavController) {
    var currentWord by remember { mutableStateOf("Loading...") }
    var userGuess by remember { mutableStateOf("") }
    var feedback by remember { mutableStateOf("") }
    var isCorrect by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }

    // 1. Function to Get a New Word
    fun fetchCard() {
        isLoading = true
        feedback = "" // Reset feedback
        userGuess = "" // Reset input
        isCorrect = false

        val req = VocabRequest(language = "German") // Fixed language for test
        RetrofitClient.apiService.generateVocab(req).enqueue(object : Callback<VocabResponse> {
            override fun onResponse(call: Call<VocabResponse>, response: Response<VocabResponse>) {
                isLoading = false
                currentWord = if (response.isSuccessful) {
                    // Python sends: { "vocabulary_word": "Apfel" }
                    response.body()?.vocabulary_word ?: "Error"
                } else {
                    "Server Error ${response.code()}"
                }
            }
            override fun onFailure(call: Call<VocabResponse>, t: Throwable) {
                isLoading = false
                currentWord = "Connection Failed"
            }
        })
    }

    // Function to Check the User's Guess
    fun checkGuess() {
        if (userGuess.isBlank()) return
        isLoading = true

        val req = VocabCheckRequest(
            target_word = currentWord,
            user_guess = userGuess,
            language = "German"
        )

        RetrofitClient.apiService.checkVocab(req).enqueue(object : Callback<VocabCheckResponse> {
            override fun onResponse(call: Call<VocabCheckResponse>, response: Response<VocabCheckResponse>) {
                isLoading = false
                if (response.isSuccessful) {
                    val result = response.body()
                    isCorrect = result?.is_correct ?: false
                    feedback = result?.feedback ?: "No feedback"
                } else {
                    feedback = "Error checking: ${response.code()}"
                }
            }
            override fun onFailure(call: Call<VocabCheckResponse>, t: Throwable) {
                isLoading = false
                feedback = "Network error"
            }
        })
    }

    // Load first card on startup
    LaunchedEffect(Unit) { fetchCard() }

    ScreenTemplate(title = "Vocab Trainer", navController = navController) {

        // The Target Word (In a real app, maybe show an Image here instead of text!)
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            Column(Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Target Word:", style = MaterialTheme.typography.labelMedium)
                Spacer(Modifier.height(8.dp))
                Text(currentWord, style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(Modifier.height(24.dp))

        // Input Field for Guess
        OutlinedTextField(
            value = userGuess,
            onValueChange = { userGuess = it },
            label = { Text("Your translation/guess") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(Modifier.height(16.dp))

        // Check Button
        Button(
            onClick = { checkGuess() },
            enabled = !isLoading && userGuess.isNotBlank(),
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Check Answer")
        }

        // Feedback Display
        if (feedback.isNotEmpty()) {
            Spacer(Modifier.height(16.dp))
            Text(
                text = feedback,
                color = if (isCorrect) Color(0xFF006400) else Color.Red, // Green if correct
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
                textAlign = TextAlign.Center
            )
        }

        Spacer(Modifier.weight(1f))

        // Next Word Button
        OutlinedButton(
            onClick = { fetchCard() },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Next Word")
        }
    }
}

// SHARED TEMPLATE
@Composable
fun ScreenTemplate(title: String, navController: NavController, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { navController.popBackStack() }) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Text(title, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        }

        // Content
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            content = content
        )
    }
}