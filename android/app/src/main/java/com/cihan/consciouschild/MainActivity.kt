package com.cihan.consciouschild

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
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
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
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
    }
    
    override fun onDestroy() {
        super.onDestroy()
        viewModel.disconnect()
    }
}

