<script lang="ts">
  import { Canvas } from '@threlte/core';
  import ThreeHouse from '$lib/components/ThreeHouse.svelte';
  import { ArrowRight, Building2, Sparkles, Home, Info } from '@lucide/svelte';

  // Svelte 5 state for room details on hover
  let activeRoom = $state<any>(null);

  function handleRoomHover(roomData: any) {
    activeRoom = roomData;
  }
</script>

<div class="landing-page animate-fade-in">
  <!-- 3D Canvas Background (Modern Villa Model) -->
  <div class="canvas-container">
    <Canvas>
      <ThreeHouse onRoomHover={handleRoomHover} />
    </Canvas>
  </div>

  <!-- UI Overlays -->
  <div class="overlay-container">
    
    <!-- Top Header -->
    <header class="landing-header">
      <div class="logo">
        <Building2 class="logo-icon" size={28} />
        <span>REA Assistant AI</span>
        <span class="version-tag">v0.1.0</span>
      </div>

      <nav class="nav-links">
        <a href="/" class="active">Overview</a>
        <a href="/dashboard">Launch App</a>
      </nav>
    </header>

    <!-- Active Hotspot Info Floating Pill (When Hovering 3D Villa Zones) -->
    {#if activeRoom}
      <div class="room-info-pill glass-panel animate-fade-in">
        <Home size={16} class="accent-icon" />
        <div class="room-text">
          <span class="room-title">{activeRoom.title}</span>
          <span class="room-sub">{activeRoom.sub}</span>
        </div>
      </div>
    {/if}

    <!-- Main Hero Content (Centered) -->
    <main class="hero-section">
      <div class="hero-card glass-panel">
        <div class="badge">
          <Sparkles size={14} class="glow-icon" />
          <span>Interactive 3D Architectural Twin</span>
        </div>
        
        <h1 class="gradient-text">Future of Real Estate. Powered by AI.</h1>
        <p class="hero-desc">
          Explore luxury architectural listings in interactive 3D. Query properties instantly, transcribe meeting transcripts, and gain real-time insight from local vector databases.
        </p>

        <div class="cta-group">
          <a href="/dashboard" class="btn-primary">
            Enter Dashboard
            <ArrowRight size={18} />
          </a>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="landing-footer">
      <p>© 2026 Real Estate Assistant AI. Deep Retrieval and Audio Transcription System.</p>
    </footer>

  </div>
</div>

<style>
  .landing-page {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background-color: #060913;
    color: #f8fafc;
  }

  .landing-page :global(.gradient-text) {
    background: linear-gradient(135deg, #ffffff 30%, #59FF00 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
  }

  .canvas-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }

  .overlay-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    pointer-events: none; /* Let clicks pass to Canvas */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2rem;
  }

  /* Make interactive DOM items capture pointer events */
  header, main, footer, a, button, .glass-panel {
    pointer-events: auto;
  }

  /* Top Header */
  .landing-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-display);
    font-size: 1.3rem;
    font-weight: 700;
    color: #f8fafc;
  }

  .logo-icon {
    color: var(--color-accent);
    filter: drop-shadow(0 0 8px var(--color-accent-glow));
  }

  .version-tag {
    font-size: 0.75rem;
    font-weight: 500;
    background: rgba(89, 255, 0, 0.15);
    color: var(--color-accent);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid rgba(89, 255, 0, 0.2);
  }

  /* Floating Room Hotspot Info Pill */
  .room-info-pill {
    position: absolute;
    top: 5.5rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px;
    border-radius: 99px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(89, 255, 0, 0.4);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 15px rgba(89, 255, 0, 0.2);
    pointer-events: auto;
    z-index: 10;
  }

  .accent-icon {
    color: #59FF00;
  }

  .room-text {
    display: flex;
    flex-direction: column;
  }

  .room-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #ffffff;
  }

  .room-sub {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .nav-links {
    display: flex;
    gap: 1.5rem;
  }

  .nav-links a {
    text-decoration: none;
    color: #94a3b8;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color var(--transition-fast);
  }

  .nav-links a:hover, .nav-links a.active {
    color: var(--color-accent);
  }

  /* Hero Section (Left Aligned for 3D Villa Visibility) */
  .hero-section {
    max-width: 540px;
    margin-top: auto;
    margin-bottom: auto;
    margin-left: 2rem;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
    gap: 1.5rem;
  }

  .hero-card {
    padding: 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }

  .badge {
    align-self: flex-start;
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(89, 255, 0, 0.1);
    border: 1px solid rgba(89, 255, 0, 0.25);
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--color-accent);
  }

  .glow-icon {
    animation: pulseGlow 2s infinite ease-in-out;
  }

  .hero-card h1 {
    font-size: 2.5rem;
    line-height: 1.15;
    font-weight: 800;
  }

  .hero-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
  }

  .cta-group {
    margin-top: 0.5rem;
    display: flex;
    justify-content: center;
  }

  /* Footer */
  .landing-footer {
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    padding-top: 1rem;
  }

  /* Responsive Design */
  @media (max-width: 1024px) {
    .overlay-container {
      overflow-y: auto;
      height: 100vh;
      height: 100dvh;
      pointer-events: auto;
      padding: 1.25rem;
    }
    
    .hero-section {
      max-width: 100%;
      margin: auto 0;
    }

    .canvas-container {
      opacity: 0.45;
    }
  }

  @media (max-width: 640px) {
    .overlay-container {
      padding: 1rem;
    }

    .landing-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;
    }

    .logo {
      font-size: 1.1rem;
    }

    .nav-links {
      width: 100%;
      justify-content: flex-start;
      gap: 1rem;
    }

    .hero-section {
      margin-left: 0;
      margin-right: 0;
      width: 100%;
      padding-top: 1rem;
      padding-bottom: 1rem;
    }

    .hero-card {
      padding: 1.25rem;
      width: 100%;
      gap: 1rem;
    }

    .hero-card h1 {
      font-size: 1.65rem;
    }

    .hero-desc {
      font-size: 0.85rem;
    }

    .cta-group {
      width: 100%;
    }

    .btn-primary {
      width: 100%;
      justify-content: center;
    }

    .room-info-pill {
      top: 6.5rem;
      width: 90%;
      justify-content: center;
    }
  }
</style>
