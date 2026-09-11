/**
 * DIRECTOR'S CUT — Streamlined Client Controller
 * Cinematic Action Recognition & Automatic Multimedia Orchestration
 */

// Screen Containers
const heroScreen = document.getElementById("heroScreen");
const cinemaScreen = document.getElementById("cinemaScreen");
const loaderOverlay = document.getElementById("loaderOverlay");

// Viewport Elements
const webcam = document.getElementById("webcam");
const debugCanvas = document.getElementById("debugCanvas");
const debugCtx = debugCanvas.getContext("2d");
const cinemaViewport = document.getElementById("cinemaViewport");
const vfxOverlay = document.getElementById("vfxOverlay");
const memeOverlay = document.getElementById("memeOverlay");
const memeImg = document.getElementById("memeImg");
const captionText = document.getElementById("captionText");
const actionNameText = document.getElementById("actionNameText");
const soundtrackName = document.getElementById("soundtrackName");

// Buttons
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const toggleAudioBtn = document.getElementById("toggleAudioBtn");
const audioIcon = document.getElementById("audioIcon");

// Notification Banner
const errorBanner = document.getElementById("errorBanner");
const errorMessage = document.getElementById("errorMessage");
const dismissErrorBtn = document.getElementById("dismissErrorBtn");

// Audio Elements
const bgmAudio = document.getElementById("bgmAudio");
const introAudio = new Audio();
let isIntroPlaying = false;
let pendingBgm = null;

// Hidden Developer Diagnostics
const debugPanel = document.getElementById("debugPanel");
const closeDebugBtn = document.getElementById("closeDebugBtn");
const dbgFps = document.getElementById("dbgFps");
const dbgLatency = document.getElementById("dbgLatency");
const dbgAction = document.getElementById("dbgAction");
const dbgConfidence = document.getElementById("dbgConfidence");
const dbgCooldown = document.getElementById("dbgCooldown");
const dbgSkeletonToggle = document.getElementById("dbgSkeletonToggle");

// Internal State
let stream = null;
let isRunning = false;
let currentAction = null;
let currentBgmTrack = null;
let isAudioMuted = false;
let isAnalyzing = false;
let frameCount = 0;
let lastFpsTime = performance.now();
let audioContext = null;

// Offscreen analysis canvas (downscaled for optimal FPS and minimal CPU)
const offCanvas = document.createElement("canvas");
offCanvas.width = 480;
offCanvas.height = 360;
const offCtx = offCanvas.getContext("2d", { willReadFrequently: true });

// ==========================================
// 1. SOUNDTRACK & AUDIO SYSTEM
// ==========================================

function initAudioContext() {
  if (!audioContext) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      audioContext = new AudioCtx();
    } catch (e) {
      console.debug("Web Audio API unavailable", e);
    }
  }
  if (audioContext && audioContext.state === "suspended") {
    audioContext.resume();
  }
}

function playCinematicSoundtrack(trackFilename, genreName, forcePlay = false) {
  pendingBgm = { trackFilename, genreName };

  // If opening start_camera_action intro is currently playing, let it play smoothly first!
  if (isIntroPlaying && !forcePlay) {
    soundtrackName.textContent = `Director: Action!`;
    return;
  }

  if (currentBgmTrack === trackFilename && !bgmAudio.paused) {
    return;
  }

  currentBgmTrack = trackFilename;
  soundtrackName.textContent = `${genreName} Track`;

  if (isAudioMuted) {
    bgmAudio.pause();
    return;
  }

  // Load from static/music/ with cache-busting timestamp
  bgmAudio.src = `/static/music/${trackFilename}?t=${Date.now()}`;
  bgmAudio.volume = 0.85;

  const playPromise = bgmAudio.play();
  if (playPromise !== undefined) {
    playPromise.catch((err) => {
      console.debug("Audio playback notice:", trackFilename, err);
      playProceduralTone(genreName);
    });
  }
}

// Procedural fallback tone in case an MP3 is missing
let synthOsc = null;
function playProceduralTone(genre) {
  if (isAudioMuted || !audioContext) return;
  try {
    if (synthOsc) {
      try { synthOsc.stop(); } catch (e) {}
    }
    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();

    let freq = 220;
    if (genre.includes("GRAND") || genre.includes("MAIN")) { freq = 261.63; osc.type = "sawtooth"; }
    else if (genre.includes("ROMANCE")) { freq = 440.0; osc.type = "sine"; }
    else if (genre.includes("SUSPENSE") || genre.includes("SPIDER")) { freq = 85.0; osc.type = "triangle"; }
    else { freq = 196.0; osc.type = "sine"; }

    osc.frequency.setValueAtTime(freq, audioContext.currentTime);
    gain.gain.setValueAtTime(0.06, audioContext.currentTime);
    osc.connect(gain);
    gain.connect(audioContext.destination);
    osc.start();
    synthOsc = osc;
  } catch (e) {}
}

toggleAudioBtn.addEventListener("click", () => {
  isAudioMuted = !isAudioMuted;
  if (isAudioMuted) {
    bgmAudio.pause();
    introAudio.pause();
    if (synthOsc) try { synthOsc.stop(); } catch (e) {}
    audioIcon.textContent = "🔇";
    toggleAudioBtn.innerHTML = `<span>🔇</span> SOUNDTRACK OFF`;
  } else {
    initAudioContext();
    if (isIntroPlaying) {
      introAudio.play().catch(() => {});
    } else if (currentBgmTrack) {
      bgmAudio.play().catch(() => {});
    }
    audioIcon.textContent = "🔊";
    toggleAudioBtn.innerHTML = `<span>🔊</span> SOUNDTRACK ON`;
  }
});

// ==========================================
// 2. CAMERA & STAGE TRANSITIONS
// ==========================================

async function startMovie() {
  hideError();
  initAudioContext();

  // 1. Show cinematic loading symbol immediately on click
  loaderOverlay.classList.remove("hidden");

  let introFinished = false;
  let cameraReady = false;

  function tryRevealStage() {
    // Only reveal the cinema screen once the start_camera_action audio finishes!
    if (introFinished && cameraReady) {
      // Hide the loading symbol
      loaderOverlay.classList.add("hidden");

      // Hide home screen and reveal active cinema screen
      heroScreen.classList.add("hidden");
      cinemaScreen.classList.remove("hidden");

      isRunning = true;
      requestAnimationFrame(analysisLoop);

      // Smoothly transition into the entrance BGM
      if (pendingBgm) {
        playCinematicSoundtrack(pendingBgm.trackFilename, pendingBgm.genreName, true);
      }
    }
  }

  // 2. Start playing "start_camera_action" audio immediately with the loading symbol
  isIntroPlaying = true;
  introAudio.pause();
  introAudio.src = `/static/music/start_camera_action.mp3?t=${Date.now()}`;
  introAudio.currentTime = 0;
  introAudio.volume = 1.0;

  // When audio finishes, mark introFinished and reveal stage
  introAudio.onended = () => {
    isIntroPlaying = false;
    introFinished = true;
    tryRevealStage();
  };

  const playPromise = introAudio.play();
  if (playPromise !== undefined) {
    playPromise.catch((err) => {
      console.debug("Intro audio notice:", err);
      // Fallback if browser audio policy blocks it
      setTimeout(() => {
        isIntroPlaying = false;
        introFinished = true;
        tryRevealStage();
      }, 1200);
    });
  }

  try {
    // 3. Reset backend session so ENTRY triggers right away
    await fetch("/api/reset", { method: "POST" }).catch(() => {});

    const constraints = {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user"
      },
      audio: false
    };

    stream = await navigator.mediaDevices.getUserMedia(constraints);
    webcam.srcObject = stream;

    await new Promise((resolve) => {
      webcam.onloadedmetadata = () => {
        webcam.play();
        resolve();
      };
    });

    debugCanvas.width = webcam.videoWidth || 640;
    debugCanvas.height = webcam.videoHeight || 480;

    cameraReady = true;
    tryRevealStage();

  } catch (err) {
    // On error, hide loader and cancel audio
    loaderOverlay.classList.add("hidden");
    introAudio.pause();
    isIntroPlaying = false;

    console.error("Camera access error:", err);
    let msg = "Director is currently blind. ";
    if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      msg += "Camera permission was denied. Please allow camera access in your browser.";
    } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
      msg += "No webcam detected. Please connect a webcam.";
    } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
      msg += "Webcam is currently in use by another application.";
    } else {
      msg += err.message || "Failed to initialize camera.";
    }
    showError(msg);
  }
}

function stopMovie() {
  isRunning = false;
  isAnalyzing = false;

  // Stop intro and hide loader
  introAudio.pause();
  introAudio.currentTime = 0;
  isIntroPlaying = false;
  pendingBgm = null;
  loaderOverlay.classList.add("hidden");

  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  webcam.srcObject = null;

  bgmAudio.pause();
  if (synthOsc) try { synthOsc.stop(); } catch (e) {}

  // Reset visual state
  cinemaViewport.className = "cinema-viewport";
  memeOverlay.classList.add("hidden");
  actionNameText.textContent = "WATCHING...";
  captionText.textContent = `"Waiting for scene to unfold..."`;
  currentAction = null;
  currentBgmTrack = null;

  // Return to clean first screen
  cinemaScreen.classList.add("hidden");
  heroScreen.classList.remove("hidden");
  debugCtx.clearRect(0, 0, debugCanvas.width, debugCanvas.height);
}

startBtn.addEventListener("click", startMovie);
stopBtn.addEventListener("click", stopMovie);

// ==========================================
// 3. COMPUTER VISION & ACTION ANALYSIS LOOP
// ==========================================

let lastAnalysisTime = 0;
const ANALYSIS_INTERVAL_MS = 120; // ~8 FPS for smooth detection with low CPU load

async function analysisLoop(now) {
  if (!isRunning) return;

  // Telemetry FPS
  frameCount++;
  if (now - lastFpsTime >= 1000) {
    const fps = (frameCount * 1000) / (now - lastFpsTime);
    dbgFps.textContent = fps.toFixed(1);
    frameCount = 0;
    lastFpsTime = now;
  }

  // Send frame for CV analysis once camera is buffered
  if (!isAnalyzing && (now - lastAnalysisTime >= ANALYSIS_INTERVAL_MS) && webcam.readyState >= 2 && webcam.videoWidth > 0) {
    lastAnalysisTime = now;
    isAnalyzing = true;

    try {
      offCtx.drawImage(webcam, 0, 0, offCanvas.width, offCanvas.height);
      const dataUrl = offCanvas.toDataURL("image/jpeg", 0.6);

      const startTime = performance.now();
      const response = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image: dataUrl,
          return_landmarks: dbgSkeletonToggle.checked
        })
      });

      const latency = Math.round(performance.now() - startTime);
      dbgLatency.textContent = `${latency} ms`;

      if (response.ok) {
        const data = await response.json();
        if (data.status === "ok") {
          applyCinematicScene(data);
        }
      }
    } catch (err) {
      console.debug("Detection notice:", err);
    } finally {
      isAnalyzing = false;
    }
  }

  requestAnimationFrame(analysisLoop);
}

// ==========================================
// 4. AUTOMATIC CINEMATIC REACTION
// ==========================================

function applyCinematicScene(data) {
  const formattedAction = data.action.replaceAll("_", " ");
  actionNameText.textContent = formattedAction;

  dbgAction.textContent = data.action;
  dbgConfidence.textContent = `${(data.confidence * 100).toFixed(0)}%`;
  if (data.smoothing) {
    dbgCooldown.textContent = data.smoothing.in_cooldown ? `${data.smoothing.cooldown_remaining}s` : "Ready";
  }

  // If action changed or scene transition requested
  if (data.action !== currentAction || data.scene_changed) {
    currentAction = data.action;

    // 1. Update comical caption
    captionText.textContent = `"${data.caption}"`;

    // 2. Apply VFX class to viewport
    cinemaViewport.className = `cinema-viewport ${data.vfx_class}`;

    // 3. Play automatic BGM track (or enqueue if intro audio is playing)
    playCinematicSoundtrack(data.bgm, data.genre);

    // 4. Update reaction meme
    if (data.meme) {
      memeImg.src = `/static/memes/${data.meme}?t=${Date.now()}`;
      memeOverlay.classList.remove("hidden");
    } else {
      memeOverlay.classList.add("hidden");
    }

    // 5. Ambient lighting shift
    shiftAmbientGlow(data.action);
  }

  // Draw debug skeleton if toggled
  if (dbgSkeletonToggle.checked && data.landmarks) {
    drawDebugLandmarks(data.landmarks);
  } else {
    debugCtx.clearRect(0, 0, debugCanvas.width, debugCanvas.height);
  }
}

function shiftAmbientGlow(action) {
  const glow = document.getElementById("ambientGlow");
  if (!glow) return;
  if (action === "ENTRY" || action === "BOTH_HANDS_UP") {
    glow.style.background = "radial-gradient(circle, rgba(245, 183, 0, 0.16) 0%, rgba(255, 132, 0, 0.06) 50%, transparent 70%)";
  } else if (action === "DRINKING_WATER" || action === "HAND_ON_HEART") {
    glow.style.background = "radial-gradient(circle, rgba(255, 64, 113, 0.16) 0%, rgba(255, 105, 180, 0.05) 50%, transparent 70%)";
  } else if (action === "RAISING_HAND" || action === "THINKING") {
    glow.style.background = "radial-gradient(circle, rgba(0, 242, 254, 0.15) 0%, rgba(0, 100, 200, 0.05) 50%, transparent 70%)";
  } else if (action === "HANDS_ON_HEAD") {
    glow.style.background = "radial-gradient(circle, rgba(255, 75, 43, 0.18) 0%, rgba(255, 65, 108, 0.06) 50%, transparent 70%)";
  } else if (action === "STANDING_UP") {
    glow.style.background = "radial-gradient(circle, rgba(255, 140, 0, 0.16) 0%, rgba(255, 180, 0, 0.05) 50%, transparent 70%)";
  } else if (action === "SITTING_DOWN") {
    glow.style.background = "radial-gradient(circle, rgba(245, 183, 0, 0.10) 0%, rgba(255, 132, 0, 0.03) 50%, transparent 70%)";
  } else if (action === "EXIT") {
    glow.style.background = "radial-gradient(circle, rgba(80, 80, 80, 0.16) 0%, rgba(0, 0, 0, 0.12) 50%, transparent 70%)";
  }
}

function drawDebugLandmarks(landmarks) {
  debugCtx.clearRect(0, 0, debugCanvas.width, debugCanvas.height);
  if (!landmarks) return;

  debugCtx.fillStyle = "#00e676";
  landmarks.forEach((pt) => {
    const x = pt.x * debugCanvas.width;
    const y = pt.y * debugCanvas.height;
    debugCtx.beginPath();
    debugCtx.arc(x, y, 3.5, 0, 2 * Math.PI);
    debugCtx.fill();
  });
}

// ==========================================
// 5. HIDDEN DEVELOPER DIAGNOSTICS (Ctrl+Shift+D)
// ==========================================

window.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.shiftKey && (e.key === "D" || e.key === "d")) {
    debugPanel.classList.toggle("hidden");
  }
});
closeDebugBtn.addEventListener("click", () => {
  debugPanel.classList.add("hidden");
});

// ==========================================
// 6. ERROR HANDLING
// ==========================================

function showError(msg) {
  errorMessage.textContent = msg;
  errorBanner.classList.remove("hidden");
}

function hideError() {
  errorBanner.classList.add("hidden");
}

dismissErrorBtn.addEventListener("click", hideError);
