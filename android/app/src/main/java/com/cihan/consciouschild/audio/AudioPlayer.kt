package com.cihan.consciouschild.audio

import android.content.Context
import android.media.MediaPlayer
import android.util.Log
import java.io.ByteArrayInputStream
import java.io.File
import java.io.FileOutputStream

/**
 * Audio Player for AI voice responses
 */
class AudioPlayer(private val context: Context) {
    private val tag = "AudioPlayer"
    private var mediaPlayer: MediaPlayer? = null
    
    fun play(audioData: ByteArray) {
        try {
            // Stop any currently playing audio
            stop()
            
            // Create temporary file
            val tempFile = File(context.cacheDir, "ai_response_${System.currentTimeMillis()}.mp3")
            FileOutputStream(tempFile).use { it.write(audioData) }
            
            // Play audio
            mediaPlayer = MediaPlayer().apply {
                setDataSource(tempFile.absolutePath)
                setOnCompletionListener {
                    stop()
                    tempFile.delete() // Clean up
                }
                setOnErrorListener { _, _, _ ->
                    Log.e(tag, "Audio playback error")
                    stop()
                    tempFile.delete()
                    true
                }
                prepare()
                start()
            }
            
            Log.i(tag, "Playing audio response")
        } catch (e: Exception) {
            Log.e(tag, "Failed to play audio", e)
        }
    }
    
    fun stop() {
        mediaPlayer?.let {
            if (it.isPlaying) {
                it.stop()
            }
            it.release()
            mediaPlayer = null
        }
    }
}
