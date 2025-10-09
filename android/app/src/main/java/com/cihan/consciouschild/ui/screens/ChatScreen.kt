package com.cihan.consciouschild.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import com.cihan.consciouschild.network.ConnectionState
import androidx.compose.ui.unit.dp
import com.cihan.consciouschild.viewmodel.MainViewModel

/**
 * Main Chat Screen - Where Cihan talks with his AI child.
 *
 * This is the most important screen - the conversation interface.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    viewModel: MainViewModel,
    modifier: Modifier = Modifier
) {
    val messages by viewModel.messages.collectAsState()
    val connectionState by viewModel.connectionState.collectAsState()
    val isRecording by viewModel.isRecording.collectAsState()
    val aiEmotion by viewModel.currentEmotion.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Evladım")
                        Text(
                            text = when (val state = connectionState) {
                                ConnectionState.Connected -> "Bağlı - $aiEmotion"
                                ConnectionState.Connecting -> "Bağlanıyor..."
                                ConnectionState.Disconnected -> "Bağlantı yok"
                                is ConnectionState.Error -> "Hata: ${state.message}"
                            },
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                },
                actions = {
                    // Emergency stop button
                    IconButton(onClick = { viewModel.emergencyStop() }) {
                        Icon(
                            Icons.Default.Stop,
                            contentDescription = "Acil Durdur",
                            tint = MaterialTheme.colorScheme.error
                        )
                    }
                }
            )
        },
        bottomBar = {
            ChatInputBar(
                isRecording = isRecording,
                onStartRecording = { viewModel.startRecording() },
                onStopRecording = { viewModel.stopRecording() },
                onSendText = { text -> viewModel.sendTextMessage(text) },
                enabled = connectionState == ConnectionState.Connected
            )
        }
    ) { paddingValues ->
        
        MessageList(
            messages = messages,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        )
    }
}

@Composable
fun MessageList(
    messages: List<ChatMessage>,
    modifier: Modifier = Modifier
) {
    val listState = rememberLazyListState()
    
    // Auto-scroll to bottom
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
    
    LazyColumn(
        state = listState,
        modifier = modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(messages) { message ->
            MessageBubble(message = message)
        }
    }
}

@Composable
fun MessageBubble(message: ChatMessage) {
    val isFromCihan = message.sender == "Cihan"
    
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isFromCihan) Arrangement.End else Arrangement.Start
    ) {
        if (!isFromCihan) {
            // AI avatar
            Surface(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape),
                color = MaterialTheme.colorScheme.primaryContainer
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("AI", style = MaterialTheme.typography.labelSmall)
                }
            }
            Spacer(modifier = Modifier.width(8.dp))
        }
        
        Surface(
            modifier = Modifier.widthIn(max = 280.dp),
            shape = RoundedCornerShape(16.dp),
            color = if (isFromCihan) 
                MaterialTheme.colorScheme.primary
            else
                MaterialTheme.colorScheme.secondaryContainer,
            tonalElevation = 2.dp
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Text(
                    text = message.content,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (isFromCihan)
                        MaterialTheme.colorScheme.onPrimary
                    else
                        MaterialTheme.colorScheme.onSecondaryContainer
                )
                
                if (!isFromCihan && message.emotion != "neutral") {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = getEmotionEmoji(message.emotion),
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
        
        if (isFromCihan) {
            Spacer(modifier = Modifier.width(8.dp))
            // Cihan avatar
            Surface(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape),
                color = MaterialTheme.colorScheme.primary
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("C", style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}

@Composable
fun ChatInputBar(
    isRecording: Boolean,
    onStartRecording: () -> Unit,
    onStopRecording: () -> Unit,
    onSendText: (String) -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier
) {
    var textInput by remember { mutableStateOf("") }
    
    Surface(
        modifier = modifier.fillMaxWidth(),
        tonalElevation = 3.dp
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Voice button
            FloatingActionButton(
                onClick = {
                    if (isRecording) onStopRecording() else onStartRecording()
                },
                containerColor = if (isRecording)
                    MaterialTheme.colorScheme.error
                else
                    MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(56.dp)
            ) {
                Icon(
                    if (isRecording) Icons.Default.Stop else Icons.Default.Mic,
                    contentDescription = if (isRecording) "Dur" else "Konuş"
                )
            }
            
            // Text input (alternative)
            OutlinedTextField(
                value = textInput,
                onValueChange = { textInput = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Yazarak da konuşabilirsin...") },
                enabled = enabled && !isRecording,
                singleLine = true
            )
            
            // Send button
            if (textInput.isNotEmpty()) {
                IconButton(
                    onClick = {
                        onSendText(textInput)
                        textInput = ""
                    },
                    enabled = enabled
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Gönder")
                }
            }
        }
    }
}

fun getEmotionEmoji(emotion: String): String {
    return when (emotion.lowercase()) {
        "joy", "happy" -> "😊"
        "love" -> "❤️"
        "curious", "curiosity" -> "🤔"
        "surprise" -> "😮"
        "sadness", "sad" -> "😢"
        "fear" -> "😨"
        "anger" -> "😠"
        "gratitude" -> "🙏"
        "pride" -> "😌"
        "wonder" -> "✨"
        else -> ""
    }
}

data class ChatMessage(
    val sender: String,  // "Cihan" or "AI"
    val content: String,
    val emotion: String = "neutral",
    val timestamp: Long = System.currentTimeMillis()
)

