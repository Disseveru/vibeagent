# Reown Android Core Setup

Use this guide to add the Reown (WalletConnect) Android Core SDK so a native Android client can connect to the same VibeAgent backend used by the web app.

## Prerequisites
- Android Studio with Java 11
- Min SDK 23+
- A Reown Project ID (reuse the `REOWN_PROJECT_ID` you already set for the web client)

## 1) Repositories
Add Reown’s repositories to your root `settings.gradle`/`build.gradle`:

```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}
```

## 2) Dependencies (with BOM)
Add the Android Bill of Materials to keep versions aligned, then pull in Core and AppKit:

```kotlin
dependencies {
    implementation(platform("com.reown:android-bom:1.4.5")) // check docs for latest
    implementation("com.reown:android-core")
    implementation("com.reown:appkit")
}
```

## 3) Initialize Reown Core
Initialize as early as possible (e.g., Application.onCreate). Use the same Project ID that the Flask app exposes via `REOWN_PROJECT_ID`:

```kotlin
import com.reown.core.CoreClient
import com.reown.core.model.ConnectionType
import com.reown.appkit.AppKit
import com.reown.appkit.Modal

val projectId = BuildConfig.REOWN_PROJECT_ID // store in gradle.properties
val appMeta = Core.Model.AppMetaData(
    name = "VibeAgent Android",
    description = "VibeAgent mobile client",
    url = "https://vibeagent.app",
    icons = listOf("https://vibeagent.app/icon.png"),
    redirect = "vibeagent://callback"
)

CoreClient.initialize(
    projectId = projectId,
    connectionType = ConnectionType.AUTOMATIC,
    application = this,
    metaData = appMeta
)

AppKit.initialize(
    init = Modal.Params.Init(core = CoreClient),
    onError = { error -> println("Reown init error: $error") }
)
```

## 4) ProGuard/R8
If you shrink/obfuscate, add:

```
-keepattributes *Annotation*
-keep class com.sun.jna.** { *; }
-keepclassmembers class com.sun.jna.** { native <methods>; *; }
-keep class uniffi.** { *; }
-dontwarn uniffi.**
-dontwarn com.sun.jna.**
```

## 5) Talking to VibeAgent
- Point your Android client at the same Flask endpoints (e.g., `/api/scan/arbitrage`, `/api/strategy/export`).
- Pass the connected wallet address from Reown into the API calls just like the web client does.
- Keep `REOWN_PROJECT_ID` consistent so WalletConnect sessions work across platforms.

## 6) Quick verification
- Launch the app and trigger wallet connect; verify a session opens in a mobile wallet.
- Call a lightweight endpoint such as `/api/wallet/state` to confirm the session is recognized by VibeAgent.
- Run an arbitrage scan and export to ensure requests complete without errors.
