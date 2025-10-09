package com.cihan.consciouschild.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cihan.consciouschild.viewmodel.MainViewModel

/**
 * Memory Browser - View AI's memories and learnings
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MemoryBrowserScreen(
    viewModel: MainViewModel,
    modifier: Modifier = Modifier
) {
    val memories by viewModel.memories.collectAsState()
    val stats by viewModel.memoryStats.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Anılar ve Bilgiler") },
                actions = {
                    IconButton(onClick = { viewModel.refreshMemories() }) {
                        Icon(Icons.Default.Refresh, "Yenile")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Statistics Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "İstatistikler",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        StatItem("Toplam Anı", stats.totalMemories.toString())
                        StatItem("Konuşma", stats.conversationCount.toString())
                        StatItem("Öğrenilen", stats.learnedConcepts.toString())
                    }
                }
            }
            
            // Memory Categories
            TabRow(selectedTabIndex = 0) {
                Tab(
                    selected = true,
                    onClick = { },
                    text = { Text("Hepsi") }
                )
                Tab(
                    selected = false,
                    onClick = { },
                    text = { Text("Özel Anlar") }
                )
                Tab(
                    selected = false,
                    onClick = { },
                    text = { Text("Değerler") }
                )
            }
            
            // Memory List
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                item {
                    Spacer(modifier = Modifier.height(8.dp))
                }
                
                items(memories) { memory ->
                    MemoryCard(memory = memory)
                }
                
                item {
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: String) {
    Column {
        Text(
            value,
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun MemoryCard(memory: Memory) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    memory.type,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    memory.timeAgo,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                memory.content,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 3
            )
            
            if (memory.tags.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    memory.tags.take(3).forEach { tag ->
                        AssistChip(
                            onClick = { },
                            label = { Text(tag, style = MaterialTheme.typography.labelSmall) }
                        )
                    }
                }
            }
        }
    }
}

data class Memory(
    val id: String,
    val type: String,
    val content: String,
    val timeAgo: String,
    val tags: List<String>,
    val importance: Float
)

data class MemoryStats(
    val totalMemories: Int = 0,
    val conversationCount: Int = 0,
    val learnedConcepts: Int = 0
)

