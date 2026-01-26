package com.example.languageapp

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

// CHAT
data class ChatRequest(val language: String, val user_msg: String, val context: List<String> = emptyList())
data class ChatResponse(val reply: String, val context: List<String>)

// VOCABULARY GENERATION
data class VocabRequest(val language: String)
data class VocabResponse(val vocabulary_word: String)

data class VocabCheckRequest(val target_word: String, val user_guess: String, val language: String)

data class VocabCheckResponse(val is_correct: Boolean, val feedback: String)

// PHONETICS (future)
data class PhoneticsRequest(val language: String, val targetPhrase: String)
data class PhoneticsResponse(val transcript: String, val score: Double, val feedback: List<String>)

interface ApiService {
    // Matches @app.post("/api/conversation")
    @POST("/api/conversation")
    fun sendMessage(@Body request: ChatRequest): Call<ChatResponse>

    // Matches @app.post("/api/vocabulary/generate")
    @POST("/api/vocabulary/generate")
    fun generateVocab(@Body request: VocabRequest): Call<VocabResponse>

    // Matches @app.post("/api/vocabulary/check")
    @POST("/api/vocabulary/check")
    fun checkVocab(@Body request: VocabCheckRequest): Call<VocabCheckResponse>

    // Legacy/Future
    @POST("/api/phonetics")
    fun checkPronunciation(@Body request: PhoneticsRequest): Call<PhoneticsResponse>
}