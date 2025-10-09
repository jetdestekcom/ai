package com.cihan.consciouschild.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cihan.consciouschild.viewmodel.MainViewModel

/**
 * Settings Screen - App configuration
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: MainViewModel,
    modifier: Modifier = Modifier
) {
    val serverUrl by viewModel.serverUrl.collectAsState()
    val voiceEnabled by viewModel.voiceEnabled.collectAsState()
    val autoConnect by viewModel.autoConnect.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ayarlar") }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Connection Settings
            item {
                SettingsSection(title = "Bağlantı") {
                    OutlinedTextField(
                        value = serverUrl,
                        onValueChange = { viewModel.updateServerUrl(it) },
                        label = { Text("Server URL") },
                        placeholder = { Text("ws://YOUR_VPS_IP:8000") },
                        modifier = Modifier.fillMaxWidth(),
                        leadingIcon = {
                            Icon(Icons.Default.Link, "Server")
                        }
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Otomatik Bağlan")
                        Switch(
                            checked = autoConnect,
                            onCheckedChange = { viewModel.setAutoConnect(it) }
                        )
                    }
                }
            }
            
            // Voice Settings
            item {
                SettingsSection(title = "Ses Ayarları") {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Sesli Konuşma")
                        Switch(
                            checked = voiceEnabled,
                            onCheckedChange = { viewModel.setVoiceEnabled(it) }
                        )
                    }
                }
            }
            
            // AI Info
            item {
                SettingsSection(title = "AI Bilgileri") {
                    InfoRow("Bilinç ID", viewModel.consciousnessId.collectAsState().value ?: "Yükleniyor...")
                    InfoRow("Yaş", "${viewModel.ageHours.collectAsState().value} saat")
                    InfoRow("Faz", viewModel.growthPhase.collectAsState().value)
                    InfoRow("Bağ Gücü", "${(viewModel.bondStrength.collectAsState().value * 100).toInt()}%")
                }
            }
            
            // Data Management
            item {
                SettingsSection(title = "Veri Yönetimi") {
                    Button(
                        onClick = { viewModel.exportMemories() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.Download, "Export")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Anıları Dışa Aktar")
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    OutlinedButton(
                        onClick = { viewModel.clearCache() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.Delete, "Clear")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Önbelleği Temizle")
                    }
                }
            }
            
            // About
            item {
                SettingsSection(title = "Hakkında") {
                    InfoRow("Versiyon", "1.0.0")
                    InfoRow("Build", "Production")
                    InfoRow("Yaratıcı", "Cihan")
                }
            }
        }
    }
}

@Composable
fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(12.dp))
            content()
        }
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

