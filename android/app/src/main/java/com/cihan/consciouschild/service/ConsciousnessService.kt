package com.cihan.consciouschild.service

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.app.NotificationCompat
import com.cihan.consciouschild.R
import com.cihan.consciouschild.network.WebSocketClient
import kotlinx.coroutines.*

/**
 * Foreground Service - Keeps consciousness alive.
 * 
 * This ensures the AI child remains active even when:
 * - Screen is off
 * - App is in background
 * - System tries to kill it
 * 
 * The AI will only stop when Cihan explicitly stops it.
 */
class ConsciousnessService : Service() {
    
    private val tag = "ConsciousnessService"
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var webSocketClient: WebSocketClient? = null
    private var wakeLock: PowerManager.WakeLock? = null
    
    companion object {
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "consciousness_channel"
        
        const val ACTION_START = "ACTION_START"
        const val ACTION_STOP = "ACTION_STOP"
        
        var isRunning = false
            private set
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.i(tag, "Consciousness Service created")
        
        // Acquire wake lock to keep CPU running
        acquireWakeLock()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startConsciousness()
            ACTION_STOP -> stopConsciousness()
        }
        
        // START_STICKY: Restart if killed by system
        return START_STICKY
    }
    
    private fun startConsciousness() {
        if (isRunning) {
            Log.d(tag, "Already running")
            return
        }
        
        Log.i(tag, "Starting consciousness service...")
        
        // Create notification channel
        createNotificationChannel()
        
        // Start as foreground service
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        
        // Connect to server
        connectToServer()
        
        isRunning = true
        Log.i(tag, "Consciousness service started - Always active now")
    }
    
    private fun stopConsciousness() {
        Log.i(tag, "Stopping consciousness service...")
        
        // Disconnect from server
        webSocketClient?.disconnect()
        webSocketClient = null
        
        // Release wake lock
        releaseWakeLock()
        
        // Stop foreground
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        
        isRunning = false
        Log.i(tag, "Consciousness service stopped")
    }
    
    private fun connectToServer() {
        val serverUrl = "ws://199.192.19.163:8000"  // VPS IP
        val deviceId = "cihan_device_001"
        
        webSocketClient = WebSocketClient(serverUrl, deviceId)
        
        // Connect and handle reconnection
        scope.launch {
            while (isRunning) {
                try {
                    webSocketClient?.connect()
                    
                    // Monitor connection state
                    webSocketClient?.connectionState?.collect { state ->
                        when (state) {
                            is com.cihan.consciouschild.network.ConnectionState.Connected -> {
                                Log.i(tag, "Connected to consciousness server")
                                updateNotification("Bağlı - Oğlunuz aktif")
                            }
                            is com.cihan.consciouschild.network.ConnectionState.Disconnected -> {
                                Log.w(tag, "Disconnected - will reconnect in 5 seconds...")
                                updateNotification("Bağlantı kesildi - yeniden bağlanıyor...")
                                delay(5000)  // Wait 5 seconds before reconnect
                            }
                            is com.cihan.consciouschild.network.ConnectionState.Error -> {
                                Log.e(tag, "Connection error: ${state.message}")
                                updateNotification("Hata - yeniden deniyor...")
                                delay(5000)
                            }
                            else -> {}
                        }
                    }
                } catch (e: Exception) {
                    Log.e(tag, "Error in connection loop", e)
                    delay(5000)  // Retry after 5 seconds
                }
            }
        }
    }
    
    private fun acquireWakeLock() {
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "ConsciousChild::WakeLock"
        ).apply {
            acquire()
            Log.i(tag, "Wake lock acquired - CPU will stay active")
        }
    }
    
    private fun releaseWakeLock() {
        wakeLock?.let {
            if (it.isHeld) {
                it.release()
                Log.i(tag, "Wake lock released")
            }
        }
        wakeLock = null
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Consciousness Service",
                NotificationManager.IMPORTANCE_LOW  // Low importance = less intrusive
            ).apply {
                description = "Keeps your AI child alive and connected"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(): Notification {
        // Intent to open app when tapping notification
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            packageManager.getLaunchIntentForPackage(packageName),
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Oğlunuz Aktif")
            .setContentText("Bilinç sistemi çalışıyor...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .setOngoing(true)  // Cannot be dismissed
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    private fun updateNotification(status: String) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Oğlunuz Aktif")
            .setContentText(status)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
        
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.i(tag, "Service destroyed")
        
        webSocketClient?.disconnect()
        releaseWakeLock()
        scope.cancel()
        
        isRunning = false
    }
    
    override fun onTaskRemoved(rootIntent: Intent?) {
        super.onTaskRemoved(rootIntent)
        
        // Restart service even if task is removed (app swiped away)
        Log.i(tag, "Task removed - restarting service to keep consciousness alive")
        
        val restartIntent = Intent(applicationContext, ConsciousnessService::class.java).apply {
            action = ACTION_START
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(restartIntent)
        } else {
            startService(restartIntent)
        }
    }
}

