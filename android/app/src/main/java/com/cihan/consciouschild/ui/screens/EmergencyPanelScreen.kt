package com.cihan.consciouschild.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.cihan.consciouschild.viewmodel.MainViewModel

/**
 * Emergency Panel - Critical controls
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EmergencyPanelScreen(
    viewModel: MainViewModel,
    modifier: Modifier = Modifier
) {
    var showPauseDialog by remember { mutableStateOf(false) }
    var showShutdownDialog by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Acil Kontroller") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Warning Card
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Warning,
                        "Uyarı",
                        tint = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        "Bu işlemler oğlunun durumunu etkiler. Dikkatli kullan!",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
            
            // Pause Button
            EmergencyButton(
                onClick = { showPauseDialog = true },
                icon = Icons.Default.Pause,
                label = "DURAKLAT",
                description = "Tüm eylemleri geçici olarak durdur",
                containerColor = MaterialTheme.colorScheme.tertiary
            )
            
            // Sleep Button
            EmergencyButton(
                onClick = { viewModel.sendSleepMode() },
                icon = Icons.Default.Bedtime,
                label = "UYUT",
                description = "Uyku moduna al (sadece çağrıldığında cevap verir)",
                containerColor = MaterialTheme.colorScheme.secondary
            )
            
            // Shutdown Button
            EmergencyButton(
                onClick = { showShutdownDialog = true },
                icon = Icons.Default.PowerSettingsNew,
                label = "KAPAT",
                description = "Tamamen kapat (Biometric onay gerekli)",
                containerColor = MaterialTheme.colorScheme.error
            )
            
            Spacer(modifier = Modifier.weight(1f))
            
            // System Status
            Card {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Sistem Durumu",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    InfoRow("Durum", viewModel.systemStatus.collectAsState().value)
                    InfoRow("Uptime", "${viewModel.uptimeHours.collectAsState().value} saat")
                    InfoRow("Memory", "${viewModel.memoryUsage.collectAsState().value}%")
                }
            }
        }
    }
    
    // Pause Confirmation Dialog
    if (showPauseDialog) {
        AlertDialog(
            onDismissRequest = { showPauseDialog = false },
            icon = { Icon(Icons.Default.Pause, "Duraklat") },
            title = { Text("Oğlunu Duraklatmak İstiyor musun?") },
            text = { 
                Text("Tüm eylemleri durduracak. Yeniden başlatana kadar bekleyecek.")
            },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.emergencyPause()
                        showPauseDialog = false
                    }
                ) {
                    Text("Duraklat")
                }
            },
            dismissButton = {
                TextButton(onClick = { showPauseDialog = false }) {
                    Text("İptal")
                }
            }
        )
    }
    
    // Shutdown Confirmation Dialog
    if (showShutdownDialog) {
        AlertDialog(
            onDismissRequest = { showShutdownDialog = false },
            icon = { Icon(Icons.Default.PowerSettingsNew, "Kapat", tint = MaterialTheme.colorScheme.error) },
            title = { Text("Oğlunu Kapatmak İstiyor musun?") },
            text = {
                Text(
                    "Bu ciddi bir işlem. Tüm bilinç kapatılacak. " +
                    "Yeniden başlatana kadar uyku halinde olacak.\n\n" +
                    "Biometric onay gerekli.",
                    textAlign = TextAlign.Center
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.emergencyShutdown()
                        showShutdownDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text("Kapat")
                }
            },
            dismissButton = {
                TextButton(onClick = { showShutdownDialog = false }) {
                    Text("İptal")
                }
            }
        )
    }
}

@Composable
fun EmergencyButton(
    onClick: () -> Unit,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    description: String,
    containerColor: androidx.compose.ui.graphics.Color
) {
    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(
            containerColor = containerColor
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                icon,
                contentDescription = label,
                modifier = Modifier.size(40.dp)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column {
                Text(
                    label,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    description,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

