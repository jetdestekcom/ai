package com.cihan.consciouschild.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.cihan.consciouschild.network.WebSocketClient
import com.cihan.consciouschild.network.ConnectionState
import com.cihan.consciouschild.network.AIMessage
import com.cihan.consciouschild.ui.screens.ChatMessage
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * Main ViewModel - Application state and business logic.
 */
class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val serverUrl = "ws://YOUR_SERVER_IP:8000"  // Configure this
    private val deviceId = "cihan_device_001"  // Unique device ID
    
    private val webSocketClient = WebSocketClient(serverUrl, deviceId)
    
    // Connection state
    val connectionState: StateFlow<ConnectionState> = webSocketClient.connectionState
    
    // Messages
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    
    // Recording state
    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()
    
    // Current AI emotion
    private val _currentEmotion = MutableStateFlow("curious")
    val currentEmotion: StateFlow<String> = _currentEmotion.asStateFlow()
    
    init {
        // Collect incoming messages
        viewModelScope.launch {
            webSocketClient.messages.collect { aiMessage ->
                handleIncomingMessage(aiMessage)
            }
        }
        
        // Auto-connect
        connect()
    }
    
    fun connect() {
        viewModelScope.launch {
            webSocketClient.connect()
        }
    }
    
    fun disconnect() {
        webSocketClient.disconnect()
    }
    
    fun sendTextMessage(text: String) {
        if (text.isBlank()) return
        
        // Add to UI
        addMessage(ChatMessage(
            sender = "Cihan",
            content = text,
            timestamp = System.currentTimeMillis()
        ))
        
        // Send to server
        viewModelScope.launch {
            webSocketClient.sendTextMessage(text)
        }
    }
    
    fun startRecording() {
        _isRecording.value = true
        // TODO: Start audio recording
    }
    
    fun stopRecording() {
        _isRecording.value = false
        // TODO: Stop recording, send audio to server
    }
    
    fun emergencyStop() {
        viewModelScope.launch {
            webSocketClient.sendControlMessage("pause")
        }
    }
    
    private fun handleIncomingMessage(aiMessage: AIMessage) {
        when (aiMessage) {
            is AIMessage.Text -> {
                addMessage(ChatMessage(
                    sender = "AI",
                    content = aiMessage.content,
                    emotion = aiMessage.emotion,
                    timestamp = aiMessage.timestamp
                ))
                _currentEmotion.value = aiMessage.emotion
            }
            
            is AIMessage.Voice -> {
                addMessage(ChatMessage(
                    sender = "AI",
                    content = aiMessage.content,
                    emotion = aiMessage.emotion,
                    timestamp = aiMessage.timestamp
                ))
                _currentEmotion.value = aiMessage.emotion
                
                // TODO: Play audio
                aiMessage.audioData?.let { playAudio(it) }
            }
            
            is AIMessage.Proactive -> {
                // AI initiated conversation
                addMessage(ChatMessage(
                    sender = "AI",
                    content = "📢 ${aiMessage.content}",
                    emotion = aiMessage.emotion,
                    timestamp = aiMessage.timestamp
                ))
            }
            
            is AIMessage.UpdateProposal -> {
                // TODO: Show update approval dialog
            }
            
            is AIMessage.System -> {
                // System message
            }
        }
    }
    
    private fun addMessage(message: ChatMessage) {
        _messages.value = _messages.value + message
    }
    
    private fun playAudio(audioData: ByteArray) {
        // TODO: Implement audio playback
    }
}

