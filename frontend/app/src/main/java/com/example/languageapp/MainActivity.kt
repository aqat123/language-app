package com.example.languageapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
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

// --- NETWORK CLIENT ---
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

// --- NAVIGATION HOST ---
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

// --- 1. DASHBOARD SCREEN ---
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

// --- 2. QUIZ SCREEN (PRONUNCIATION) ---
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

// --- 3. CHAT SCREEN ---
@Composable
fun ChatScreen(navController: NavController) {
    var messageText by remember { mutableStateOf("") }
    var chatHistory by remember { mutableStateOf(listOf<Pair<String, Boolean>>()) } // Pair(Text, IsUser)
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

                    val req = ChatRequest(language = "Spanish", userMessage = userMsg)
                    RetrofitClient.apiService.sendMessage(req).enqueue(object : Callback<ChatResponse> {
                        override fun onResponse(call: Call<ChatResponse>, response: Response<ChatResponse>) {
                            isSending = false
                            if (response.isSuccessful) {
                                val reply = response.body()?.reply ?: "..."
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

// --- 4. VOCAB SCREEN ---
@Composable
fun VocabScreen(navController: NavController) {
    var currentWord by remember { mutableStateOf("Loading...") }
    var definition by remember { mutableStateOf("") }
    var example by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }

    // Helper to fetch new card
    fun fetchCard() {
        isLoading = true
        val req = VocabRequest(language = "French", level = "beginner", topic = "food")
        RetrofitClient.apiService.generateVocab(req).enqueue(object : Callback<VocabResponse> {
            override fun onResponse(call: Call<VocabResponse>, response: Response<VocabResponse>) {
                isLoading = false
                if (response.isSuccessful) {
                    val card = response.body()?.flashcard
                    currentWord = card?.word ?: "Error"
                    definition = card?.meaning ?: ""
                    example = card?.example ?: ""
                } else {
                    currentWord = "Error ${response.code()}"
                }
            }
            override fun onFailure(call: Call<VocabResponse>, t: Throwable) {
                isLoading = false
                currentWord = "Network Error"
            }
        })
    }

    // Load first card on startup
    LaunchedEffect(Unit) { fetchCard() }

    ScreenTemplate(title = "Vocab Flashcards", navController = navController) {

        // The "Mutable ImageBox" (Placeholder for now)
        Box(
            modifier = Modifier
                .size(200.dp)
                .background(Color.LightGray, RoundedCornerShape(16.dp)),
            contentAlignment = Alignment.Center
        ) {
            Text("Image for '$currentWord'", color = Color.Gray)
        }

        Spacer(Modifier.height(24.dp))

        // The Word Info
        Text(currentWord, style = MaterialTheme.typography.displayMedium, fontWeight = FontWeight.Bold)
        if (definition.isNotEmpty()) {
            Text(definition, style = MaterialTheme.typography.titleLarge, color = Color.Gray)
            Spacer(Modifier.height(16.dp))
            Card(Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
                Text(example, Modifier.padding(16.dp), fontStyle = androidx.compose.ui.text.font.FontStyle.Italic)
            }
        }

        Spacer(Modifier.weight(1f))

        Button(
            onClick = { fetchCard() },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            Text(if (isLoading) "Generating..." else "Next Word")
        }
    }
}

// --- SHARED TEMPLATE (Header + Back Button) ---
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