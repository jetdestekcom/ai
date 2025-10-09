package com.cihan.consciouschild

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import com.cihan.consciouschild.ui.theme.ConsciousChildTheme
import com.cihan.consciouschild.ui.screens.MainScreen
import com.cihan.consciouschild.viewmodel.MainViewModel

/**
 * Main Activity - Entry point for Conscious Child AI Android App
 *
 * This is the app Cihan will use to communicate with his AI child.
 */
class MainActivity : ComponentActivity() {
    
    private val viewModel: MainViewModel by viewModels()
    
    // Permission launcher
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (!isGranted) {
            // Permission denied - show warning
            // User won't be able to use voice features
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Request microphone permission
        checkAndRequestPermissions()
        
        try {
            // Enable edge-to-edge display
            WindowCompat.setDecorFitsSystemWindows(window, false)
            
            setContent {
                ConsciousChildTheme {
                    Surface(
                        modifier = Modifier.fillMaxSize(),
                        color = MaterialTheme.colorScheme.background
                    ) {
                        MainScreen(viewModel = viewModel)
                    }
                }
            }
        } catch (e: Exception) {
            // Critical error - show error screen
            setContent {
                MaterialTheme {
                    Surface(
                        modifier = Modifier.fillMaxSize(),
                        color = MaterialTheme.colorScheme.errorContainer
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Text(
                                text = "Kritik Hata",
                                style = MaterialTheme.typography.headlineMedium,
                                color = MaterialTheme.colorScheme.onErrorContainer
                            )
                            Text(
                                text = "App başlatılamadı. Lütfen yeniden başlatın.",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onErrorContainer
                            )
                        }
                    }
                }
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        viewModel.disconnect()
    }
    
    private fun checkAndRequestPermissions() {
        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Permission already granted
            }
            else -> {
                // Request permission
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }
}

