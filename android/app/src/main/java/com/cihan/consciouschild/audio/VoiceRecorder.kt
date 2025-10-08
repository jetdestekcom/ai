package com.cihan.consciouschild.audio

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import java.io.File
import java.io.FileInputStream

/**
 * Voice Recorder - Records Cihan's voice.
 *
 * Captures audio for sending to AI.
 */
class VoiceRecorder(private val context: Context) {
    
    private var mediaRecorder: MediaRecorder? = null
    private var outputFile: File? = null
    
    /**
     * Start recording.
     */
    fun startRecording(): File {
        // Create output file
        outputFile = File(context.cacheDir, "recording_${System.currentTimeMillis()}.opus")
        
        mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context)
        } else {
            @Suppress("DEPRECATION")
            MediaRecorder()
        }.apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.OGG)
            setAudioEncoder(MediaRecorder.AudioEncoder.OPUS)
            setAudioEncodingBitRate(24000)
            setAudioSamplingRate(16000)
            setOutputFile(outputFile!!.absolutePath)
            
            prepare()
            start()
        }
        
        return outputFile!!
    }
    
    /**
     * Stop recording and get audio data.
     */
    fun stopRecording(): ByteArray {
        mediaRecorder?.apply {
            stop()
            release()
        }
        mediaRecorder = null
        
        // Read file
        val audioData = outputFile?.let { file ->
            FileInputStream(file).use { it.readBytes() }
        } ?: byteArrayOf()
        
        // Cleanup
        outputFile?.delete()
        
        return audioData
    }
    
    /**
     * Cancel recording.
     */
    fun cancelRecording() {
        mediaRecorder?.apply {
            stop()
            release()
        }
        mediaRecorder = null
        outputFile?.delete()
    }
}

/**
 * Audio Player - Plays AI's voice.
 */
class AudioPlayer(private val context: Context) {
    
    private var mediaPlayer: android.media.MediaPlayer? = null
    
    /**
     * Play audio data.
     */
    fun play(audioData: ByteArray, onComplete: () -> Unit = {}) {
        // Save to temp file
        val tempFile = File(context.cacheDir, "playback_${System.currentTimeMillis()}.wav")
        tempFile.writeBytes(audioData)
        
        mediaPlayer = android.media.MediaPlayer().apply {
            setDataSource(tempFile.absolutePath)
            setOnCompletionListener {
                onComplete()
                tempFile.delete()
                release()
            }
            prepare()
            start()
        }
    }
    
    /**
     * Stop playback.
     */
    fun stop() {
        mediaPlayer?.apply {
            if (isPlaying) stop()
            release()
        }
        mediaPlayer = null
    }
}

