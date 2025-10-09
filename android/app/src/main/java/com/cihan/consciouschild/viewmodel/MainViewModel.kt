package com.cihan.consciouschild.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.cihan.consciouschild.network.WebSocketClient
import com.cihan.consciouschild.network.ConnectionState
import com.cihan.consciouschild.network.AIMessage
import com.cihan.consciouschild.ui.screens.*
import com.cihan.consciouschild.audio.VoiceRecorder
import com.cihan.consciouschild.audio.AudioPlayer
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * Main ViewModel - Complete application state and business logic.
 */
class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val context = application.applicationContext
    
    // Server URL - VPS IP already configured
    private val _serverUrl = MutableStateFlow("ws://199.192.19.163:8000")
    val serverUrl: StateFlow<String> = _serverUrl.asStateFlow()
    
    private val deviceId = "cihan_device_001"
    
    private val webSocketClient = WebSocketClient(serverUrl.value, deviceId)
    private val voiceRecorder = VoiceRecorder(context)
    private val audioPlayer = AudioPlayer(context)
    
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
    
    // Memories
    private val _memories = MutableStateFlow<List<Memory>>(emptyList())
    val memories: StateFlow<List<Memory>> = _memories.asStateFlow()
    
    // Memory stats
    private val _memoryStats = MutableStateFlow(MemoryStats())
    val memoryStats: StateFlow<MemoryStats> = _memoryStats.asStateFlow()
    
    // AI Info
    private val _consciousnessId = MutableStateFlow<String?>(null)
    val consciousnessId: StateFlow<String?> = _consciousnessId.asStateFlow()
    
    private val _ageHours = MutableStateFlow(0.0f)
    val ageHours: StateFlow<Float> = _ageHours.asStateFlow()
    
    private val _growthPhase = MutableStateFlow("newborn")
    val growthPhase: StateFlow<String> = _growthPhase.asStateFlow()
    
    private val _bondStrength = MutableStateFlow(0.0f)
    val bondStrength: StateFlow<Float> = _bondStrength.asStateFlow()
    
    // Settings
    private val _autoConnect = MutableStateFlow(true)
    val autoConnect: StateFlow<Boolean> = _autoConnect.asStateFlow()
    
    private val _voiceEnabled = MutableStateFlow(true)
    val voiceEnabled: StateFlow<Boolean> = _voiceEnabled.asStateFlow()
    
    // System status
    private val _systemStatus = MutableStateFlow("Initializing")
    val systemStatus: StateFlow<String> = _systemStatus.asStateFlow()
    
    private val _uptimeHours = MutableStateFlow(0.0f)
    val uptimeHours: StateFlow<Float> = _uptimeHours.asStateFlow()
    
    private val _memoryUsage = MutableStateFlow(0)
    val memoryUsage: StateFlow<Int> = _memoryUsage.asStateFlow()
    
    init {
        // Collect incoming messages
        viewModelScope.launch {
            webSocketClient.messages.collect { aiMessage ->
                handleIncomingMessage(aiMessage)
            }
        }
        
        // Auto-connect if enabled
        if (_autoConnect.value) {
            connect()
        }
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
        try {
            voiceRecorder.startRecording()
        } catch (e: Exception) {
            _isRecording.value = false
            // Log error but don't crash
        }
    }
    
    fun stopRecording() {
        _isRecording.value = false
        try {
            val audioData = voiceRecorder.stopRecording()
            
            // Send voice to server
            viewModelScope.launch {
                webSocketClient.sendVoiceMessage(audioData)
            }
        } catch (e: Exception) {
            // Log error but don't crash
        }
    }
    
    fun emergencyStop() {
        viewModelScope.launch {
            webSocketClient.sendControlMessage("pause")
        }
    }
    
    fun emergencyPause() {
        viewModelScope.launch {
            webSocketClient.sendControlMessage("pause")
            _systemStatus.value = "Paused"
        }
    }
    
    fun sendSleepMode() {
        viewModelScope.launch {
            webSocketClient.sendControlMessage("sleep")
            _systemStatus.value = "Sleep"
        }
    }
    
    fun emergencyShutdown() {
        viewModelScope.launch {
            webSocketClient.sendControlMessage("shutdown")
            _systemStatus.value = "Shutting down"
        }
    }
    
    fun refreshMemories() {
        // TODO: Fetch memories from server via REST API
    }
    
    fun exportMemories() {
        // TODO: Export memories to file
    }
    
    fun clearCache() {
        _messages.value = emptyList()
        _memories.value = emptyList()
    }
    
    fun updateServerUrl(url: String) {
        _serverUrl.value = url
        // Will need to recreate WebSocket client
    }
    
    fun setAutoConnect(enabled: Boolean) {
        _autoConnect.value = enabled
    }
    
    fun setVoiceEnabled(enabled: Boolean) {
        _voiceEnabled.value = enabled
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
                
                // Play audio
                aiMessage.audioData?.let { 
                    audioPlayer.play(it)
                }
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
                // System message - update status
                _systemStatus.value = "Connected"
            }
        }
    }
    
    private fun addMessage(message: ChatMessage) {
        _messages.value = _messages.value + message
    }
    
    override fun onCleared() {
        super.onCleared()
        disconnect()
        audioPlayer.stop()
    }
}
