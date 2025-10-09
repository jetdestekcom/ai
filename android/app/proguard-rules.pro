# Conscious Child AI - ProGuard Rules

# Keep all model classes
-keep class com.cihan.consciouschild.network.** { *; }
-keep class com.cihan.consciouschild.ui.screens.** { *; }

# WebSocket
-keep class io.ktor.** { *; }
-dontwarn io.ktor.**

# Moshi
-keep class com.squareup.moshi.** { *; }
-dontwarn com.squareup.moshi.**

# Kotlin
-keep class kotlin.** { *; }
-keep class kotlinx.** { *; }

# AndroidX
-keep class androidx.** { *; }
-dontwarn androidx.**

