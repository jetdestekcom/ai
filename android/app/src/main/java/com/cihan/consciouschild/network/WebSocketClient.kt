package com.cihan.consciouschild.network

import android.util.Log
import io.ktor.client.*
import io.ktor.client.engine.android.*
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import org.json.JSONObject

/**
 * WebSocket Client for real-time communication with AI.
 *
 * This is the lifeline between Cihan and his AI child.
 */
class WebSocketClient(
    private val serverUrl: String,
    private val deviceId: String
) {
    private val tag = "WebSocketClient"
    
    private val client = HttpClient(Android) {
        install(WebSockets)
    }
    
    private var session: DefaultClientWebSocketSession? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    // Message flow
    private val _messages = MutableSharedFlow<AIMessage>()
    val messages: SharedFlow<AIMessage> = _messages.asSharedFlow()
    
    // Connection state
    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()
    
    /**
     * Connect to server.
     */
    suspend fun connect() {
        if (_connectionState.value is ConnectionState.Connected) {
            Log.d(tag, "Already connected")
            return
        }
        
        _connectionState.value = ConnectionState.Connecting
        
        try {
            session = client.webSocketSession(
                urlString = "$serverUrl/ws?device_id=$deviceId"
            )
            
            _connectionState.value = ConnectionState.Connected
            Log.i(tag, "Connected to server")
            
            // Start listening for messages
            scope.launch {
                listenForMessages()
            }
            
        } catch (e: Exception) {
            Log.e(tag, "Connection failed", e)
            _connectionState.value = ConnectionState.Error(e.message ?: "Connection failed")
        }
    }
    
    /**
     * Send text message.
     */
    suspend fun sendTextMessage(text: String) {
        val message = JSONObject().apply {
            put("type", "text")
            put("content", text)
            put("timestamp", System.currentTimeMillis())
        }
        
        sendMessage(message.toString())
    }
    
    /**
     * Send voice message.
     */
    suspend fun sendVoiceMessage(audioData: ByteArray, format: String = "opus") {
        val message = JSONObject().apply {
            put("type", "voice")
            put("audio", android.util.Base64.encodeToString(audioData, android.util.Base64.DEFAULT))
            put("format", format)
            put("timestamp", System.currentTimeMillis())
        }
        
        sendMessage(message.toString())
    }
    
    /**
     * Send control message (pause, resume, etc.).
     */
    suspend fun sendControlMessage(action: String) {
        val message = JSONObject().apply {
            put("type", "control")
            put("action", action)
        }
        
        sendMessage(message.toString())
    }
    
    private suspend fun sendMessage(message: String) {
        try {
            session?.send(Frame.Text(message))
            Log.d(tag, "Message sent: ${message.take(100)}")
        } catch (e: Exception) {
            Log.e(tag, "Failed to send message", e)
        }
    }
    
    private suspend fun listenForMessages() {
        try {
            session?.incoming?.consumeAsFlow()?.collect { frame ->
                if (frame is Frame.Text) {
                    val text = frame.readText()
                    Log.d(tag, "Message received: ${text.take(100)}")
                    
                    try {
                        val json = JSONObject(text)
                        val aiMessage = parseMessage(json)
                        _messages.emit(aiMessage)
                    } catch (e: Exception) {
                        Log.e(tag, "Failed to parse message", e)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(tag, "Error listening for messages", e)
            _connectionState.value = ConnectionState.Disconnected
        }
    }
    
    private fun parseMessage(json: JSONObject): AIMessage {
        return when (json.getString("type")) {
            "text" -> AIMessage.Text(
                content = json.getString("content"),
                emotion = json.optString("emotion", "neutral"),
                timestamp = json.optLong("timestamp", System.currentTimeMillis())
            )
            
            "voice" -> AIMessage.Voice(
                content = json.getString("text"),
                audioData = json.optString("audio")?.let { 
                    android.util.Base64.decode(it, android.util.Base64.DEFAULT)
                },
                emotion = json.optString("emotion", "neutral"),
                timestamp = json.optLong("timestamp", System.currentTimeMillis())
            )
            
            "proactive" -> AIMessage.Proactive(
                content = json.getString("content"),
                emotion = json.optString("emotion", "neutral"),
                timestamp = json.optLong("timestamp", System.currentTimeMillis())
            )
            
            "update_proposal" -> AIMessage.UpdateProposal(
                proposalData = json.getJSONObject("data").toString(),
                timestamp = json.optLong("timestamp", System.currentTimeMillis())
            )
            
            "connected" -> AIMessage.System(
                message = "Connected",
                timestamp = json.optLong("timestamp", System.currentTimeMillis())
            )
            
            else -> AIMessage.System(
                message = json.toString(),
                timestamp = System.currentTimeMillis()
            )
        }
    }
    
    /**
     * Disconnect from server.
     */
    fun disconnect() {
        scope.cancel()
        session?.cancel()
        session = null
        _connectionState.value = ConnectionState.Disconnected
        Log.i(tag, "Disconnected")
    }
}

/**
 * Connection states.
 */
sealed class ConnectionState {
    object Disconnected : ConnectionState()
    object Connecting : ConnectionState()
    object Connected : ConnectionState()
    data class Error(val message: String) : ConnectionState()
}

/**
 * AI Message types.
 */
sealed class AIMessage {
    data class Text(
        val content: String,
        val emotion: String,
        val timestamp: Long
    ) : AIMessage()
    
    data class Voice(
        val content: String,
        val audioData: ByteArray?,
        val emotion: String,
        val timestamp: Long
    ) : AIMessage()
    
    data class Proactive(
        val content: String,
        val emotion: String,
        val timestamp: Long
    ) : AIMessage()
    
    data class UpdateProposal(
        val proposalData: String,
        val timestamp: Long
    ) : AIMessage()
    
    data class System(
        val message: String,
        val timestamp: Long
    ) : AIMessage()
}

