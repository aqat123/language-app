package com.example.languageapp

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

// Data Models
data class GreetingResponse(val message: String)

// Vocabulary (Q&A framework)
data class VocabRequest(val language: String, val level: String, val topic: String)
data class VocabResponse(val flashcard: FlashcardItem)
data class FlashcardItem(val word: String, val meaning: String, val example: String)

// Chatting: straightforward.
data class ChatRequest(val language: String, val userMessage: String, val context: List<String> = emptyList())
data class ChatResponse(val reply: String, val context: List<String>)

// should discuss this :)
data class PhoneticsRequest(val language: String, val targetPhrase: String)
data class PhoneticsResponse(val transcript: String, val score: Double, val feedback: List<String>)

// API behavior
interface ApiService {
    @GET("/api/greeting")
    fun getGreeting(): Call<GreetingResponse>

    @POST("/api/vocabulary/generate")
    fun generateVocab(@Body request: VocabRequest): Call<VocabResponse>

    @POST("/api/conversation")
    fun sendMessage(@Body request: ChatRequest): Call<ChatResponse>

    @POST("/api/phonetics")
    fun checkPronunciation(@Body request: PhoneticsRequest): Call<PhoneticsResponse>
}