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
        try {
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
        } catch (e: Exception) {
            // Clean up on error
            mediaRecorder?.release()
            mediaRecorder = null
            outputFile?.delete()
            outputFile = null
            throw e
        }
    }
    
    /**
     * Stop recording and get audio data.
     */
    fun stopRecording(): ByteArray {
        try {
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
        } catch (e: Exception) {
            // Clean up on error
            mediaRecorder?.release()
            mediaRecorder = null
            outputFile?.delete()
            outputFile = null
            return byteArrayOf()
        }
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
