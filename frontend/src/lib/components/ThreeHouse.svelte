<script lang="ts">
  import { T, useTask, useThrelte } from '@threlte/core';
  import { OrbitControls, HTML } from '@threlte/extras';
  import * as THREE from 'three';
  import { onMount } from 'svelte';

  let { onRoomHover = (room: any) => {} } = $props();

  const { scene } = useThrelte();

  // Set rich twilight architectural sky background for high contrast & luxury lighting
  scene.background = new THREE.Color('#080d1a');

  // Interactive room state
  let activeHover = $state<string | null>(null);

  // Procedural Canvas Textures
  let woodSlatMap = $state<THREE.CanvasTexture | null>(null);
  let stackedStoneMap = $state<THREE.CanvasTexture | null>(null);
  let latticeMap = $state<THREE.CanvasTexture | null>(null);
  let grassMap = $state<THREE.CanvasTexture | null>(null);
  let drivewayMap = $state<THREE.CanvasTexture | null>(null);

  // Interactive Villa Room Hotspots
  const villaHotspots = [
    { 
      id: 'master', 
      pos: [-2, 7.8, 3.5] as [number, number, number], 
      title: 'MASTER SUITE & BALCONY', 
      sub: '520 sq ft • Wood Clad • Ocean View',
      color: '#eab308'
    },
    { 
      id: 'carport', 
      pos: [6.5, 3.2, 3] as [number, number, number], 
      title: 'CARPORT & PORCH', 
      sub: '2-Car Covered Garage • EV Charging',
      color: '#38bdf8'
    },
    { 
      id: 'living', 
      pos: [-3.5, 2.2, 4.2] as [number, number, number], 
      title: 'OPEN LIVING & DINING', 
      sub: 'Stacking Stone Accent Wall • Floor Windows',
      color: '#59FF00'
    },
    { 
      id: 'pergola', 
      pos: [5.5, 10.2, 0.5] as [number, number, number], 
      title: 'PERGOLA & SUN DECK', 
      sub: 'Lattice Privacy Screen • Hanging Flora',
      color: '#a855f7'
    }
  ];

  onMount(() => {
    generateVillaTextures();
  });

  function generateVillaTextures() {
    if (typeof document === 'undefined') return;

    // 1. Horizontal Wood Slat Texture (Teak / Oak Planks)
    const wCanvas = document.createElement('canvas');
    wCanvas.width = 512;
    wCanvas.height = 512;
    const wCtx = wCanvas.getContext('2d')!;
    wCtx.fillStyle = '#7a3e1d';
    wCtx.fillRect(0, 0, 512, 512);

    const slatH = 20;
    for (let y = 0; y < 512; y += slatH) {
      const grad = wCtx.createLinearGradient(0, y, 0, y + slatH);
      grad.addColorStop(0, '#9e562d');
      grad.addColorStop(0.5, '#7a3e1d');
      grad.addColorStop(1, '#572a11');
      wCtx.fillStyle = grad;
      wCtx.fillRect(0, y, 512, slatH - 3);

      wCtx.fillStyle = '#2e1406';
      wCtx.fillRect(0, y + slatH - 3, 512, 3);
    }
    const wTex = new THREE.CanvasTexture(wCanvas);
    wTex.wrapS = THREE.RepeatWrapping;
    wTex.wrapT = THREE.RepeatWrapping;
    wTex.repeat.set(3, 3);
    woodSlatMap = wTex;

    // 2. Stacked Stone Tile Texture (Ground Floor Accent)
    const sCanvas = document.createElement('canvas');
    sCanvas.width = 512;
    sCanvas.height = 512;
    const sCtx = sCanvas.getContext('2d')!;
    sCtx.fillStyle = '#8c8479';
    sCtx.fillRect(0, 0, 512, 512);

    const stoneH = 14;
    let seed = 456;
    for (let y = 0; y < 512; y += stoneH) {
      let x = (y % 28 === 0) ? 0 : 18;
      while (x < 512) {
        const stoneW = 30 + Math.abs(Math.sin(seed++)) * 50;
        const colors = ['#a3998e', '#80776c', '#696259', '#bfae9e', '#524b43'];
        const color = colors[Math.floor((Math.sin(seed++) + 1) * 2)];
        sCtx.fillStyle = color;
        sCtx.fillRect(x, y, stoneW - 2, stoneH - 2);
        x += stoneW;
      }
    }
    const sTex = new THREE.CanvasTexture(sCanvas);
    sTex.wrapS = THREE.RepeatWrapping;
    sTex.wrapT = THREE.RepeatWrapping;
    sTex.repeat.set(2, 2);
    stackedStoneMap = sTex;

    // 3. White Lattice Screen Pattern
    const lCanvas = document.createElement('canvas');
    lCanvas.width = 256;
    lCanvas.height = 256;
    const lCtx = lCanvas.getContext('2d')!;
    lCtx.fillStyle = '#ffffff';
    lCtx.fillRect(0, 0, 256, 256);
    lCtx.fillStyle = '#334155';
    const holeSize = 12;
    const gap = 24;
    for (let x = 6; x < 256; x += gap) {
      for (let y = 6; y < 256; y += gap) {
        lCtx.fillRect(x, y, holeSize, holeSize);
      }
    }
    const lTex = new THREE.CanvasTexture(lCanvas);
    lTex.wrapS = THREE.RepeatWrapping;
    lTex.wrapT = THREE.RepeatWrapping;
    lTex.repeat.set(3, 6);
    latticeMap = lTex;

    // 4. Concrete Paved Driveway Texture
    const dCanvas = document.createElement('canvas');
    dCanvas.width = 512;
    dCanvas.height = 512;
    const dCtx = dCanvas.getContext('2d')!;
    dCtx.fillStyle = '#d8dce3';
    dCtx.fillRect(0, 0, 512, 512);
    dCtx.strokeStyle = '#a8b0bd';
    dCtx.lineWidth = 2;
    const tileS = 64;
    for (let x = 0; x <= 512; x += tileS) {
      dCtx.beginPath(); dCtx.moveTo(x, 0); dCtx.lineTo(x, 512); dCtx.stroke();
      dCtx.beginPath(); dCtx.moveTo(0, x); dCtx.lineTo(512, x); dCtx.stroke();
    }
    const dTex = new THREE.CanvasTexture(dCanvas);
    dTex.wrapS = THREE.RepeatWrapping;
    dTex.wrapT = THREE.RepeatWrapping;
    dTex.repeat.set(10, 10);
    drivewayMap = dTex;

    // 5. Lush Green Lawn Grass Texture
    const gCanvas = document.createElement('canvas');
    gCanvas.width = 512;
    gCanvas.height = 512;
    const gCtx = gCanvas.getContext('2d')!;
    gCtx.fillStyle = '#4d7c0f';
    gCtx.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) {
      const gx = Math.random() * 512;
      const gy = Math.random() * 512;
      gCtx.fillStyle = Math.random() > 0.5 ? '#65a30d' : '#3f6212';
      gCtx.fillRect(gx, gy, 3, 3);
    }
    const gTex = new THREE.CanvasTexture(gCanvas);
    gTex.wrapS = THREE.RepeatWrapping;
    gTex.wrapT = THREE.RepeatWrapping;
    gTex.repeat.set(16, 16);
    grassMap = gTex;
  }

  function handleHotspotHover(id: string | null) {
    activeHover = id;
    const found = villaHotspots.find(h => h.id === id);
    onRoomHover(found || null);
  }
</script>

<!-- Soft Twilight Atmospheric Fog -->
<T.FogExp2 color="#080d1a" density={0.007} />

<!-- Realistic Golden Afternoon Sunlight & Sky Illumination -->
<T.HemisphereLight skyColor="#38bdf8" groundColor="#0f172a" intensity={1.2} />

<!-- Main Golden Hour Directional Sunlight -->
<T.DirectionalLight
  position={[40, 50, 30]}
  intensity={3.2}
  color="#fff1d6"
  castShadow
/>

<!-- Soft Ambient Blue Fill Light -->
<T.DirectionalLight
  position={[-30, 35, -25]}
  intensity={0.9}
  color="#bae6fd"
/>

<!-- Warm Interior Window Glow Lights -->
<T.PointLight position={[-3, 2.5, 2]} intensity={4.5} color="#fef08a" distance={12} />
<T.PointLight position={[-2, 6.5, 2]} intensity={4.5} color="#fde047" distance={14} />
<T.PointLight position={[4, 6.5, 0]} intensity={4.0} color="#fed7aa" distance={12} />


<!-- ================= GROUND, LAWN & PAVED DRIVEWAY ================= -->
<T.Group position={[0, 0, 0]}>
  <!-- Front Paved Driveway Plaza -->
  {#if drivewayMap}
    <T.Mesh position={[0, 0, 8]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <T.PlaneGeometry args={[45, 28]} />
      <T.MeshStandardMaterial map={drivewayMap} roughness={0.4} metalness={0.1} />
    </T.Mesh>
  {/if}

  <!-- Surrounding Green Lawn Grass -->
  {#if grassMap}
    <T.Mesh position={[0, -0.05, -10]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <T.PlaneGeometry args={[110, 50]} />
      <T.MeshStandardMaterial map={grassMap} roughness={0.8} />
    </T.Mesh>
    <!-- Left Lawn Extension -->
    <T.Mesh position={[-32, -0.05, 5]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <T.PlaneGeometry args={[25, 60]} />
      <T.MeshStandardMaterial map={grassMap} roughness={0.8} />
    </T.Mesh>
    <!-- Right Lawn Extension -->
    <T.Mesh position={[32, -0.05, 5]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <T.PlaneGeometry args={[25, 60]} />
      <T.MeshStandardMaterial map={grassMap} roughness={0.8} />
    </T.Mesh>
  {/if}
</T.Group>


<!-- ================= 3D MODERN LUXURY VILLA STRUCTURE ================= -->
<T.Group position={[0, 0, 0]}>

  <!-- ---------------- 1. GROUND FLOOR LEVEL (Y:0 to Y:4.2) ---------------- -->
  
  <!-- Left Living Area Body (Stacked Stone Accent Wall) -->
  {#if stackedStoneMap}
    <T.Mesh position={[-4, 2.1, 0.5]} castShadow receiveShadow>
      <T.BoxGeometry args={[11, 4.2, 9]} />
      <T.MeshStandardMaterial
        map={stackedStoneMap}
        roughness={0.7}
        metalness={0.1}
      />
    </T.Mesh>
  {/if}

  <!-- White Concrete Perimeter Band / Box Frame (Ground Floor Left) -->
  <T.Mesh position={[-4, 2.1, 5.1]} castShadow>
    <T.BoxGeometry args={[11.6, 4.3, 0.3]} />
    <T.MeshStandardMaterial color="#f8fafc" roughness={0.25} />
  </T.Mesh>

  <!-- Large Picture Glass Windows (Ground Floor Left) -->
  <T.Mesh position={[-4.5, 2.0, 5.28]}>
    <T.BoxGeometry args={[8.5, 2.6, 0.1]} />
    <T.MeshPhysicalMaterial
      color="#0f172a"
      transmission={0.85}
      transparent
      opacity={0.85}
      roughness={0.05}
      clearcoat={1.0}
    />
  </T.Mesh>
  <!-- Window Dark Frames -->
  {#each [-7.5, -4.5, -1.5] as wx}
    <T.Mesh position={[wx, 2.0, 5.34]}>
      <T.BoxGeometry args={[0.15, 2.65, 0.08]} />
      <T.MeshStandardMaterial color="#1e293b" metalness={0.8} />
    </T.Mesh>
  {/each}

  <!-- Main Wooden Double Entrance Door -->
  <T.Mesh position={[4.2, 1.8, 4.8]}>
    <T.BoxGeometry args={[1.8, 3.4, 0.2]} />
    <T.MeshStandardMaterial color="#572a11" roughness={0.4} />
  </T.Mesh>
  <!-- Door Handles -->
  <T.Mesh position={[3.5, 1.8, 4.95]}>
    <T.BoxGeometry args={[0.06, 0.8, 0.08]} />
    <T.MeshStandardMaterial color="#e2e8f0" metalness={0.9} roughness={0.1} />
  </T.Mesh>

  <!-- Carport Support Pillar & Overhang Roof -->
  <T.Mesh position={[8.5, 2.0, 5.0]}>
    <T.BoxGeometry args={[0.7, 4.0, 0.7]} />
    <T.MeshStandardMaterial color="#ffffff" roughness={0.2} />
  </T.Mesh>
  <T.Mesh position={[5.8, 4.15, 3.0]} castShadow>
    <T.BoxGeometry args={[8.0, 0.35, 7.5]} />
    <T.MeshStandardMaterial color="#f1f5f9" roughness={0.25} />
  </T.Mesh>

  <!-- ---------------- 3D LUXURY SUV / CAR PARKED UNDER CARPORT ---------------- -->
  <T.Group position={[6.0, 0.75, 3.0]}>
    <!-- Car Body Base -->
    <T.Mesh position={[0, 0.5, 0]} castShadow>
      <T.BoxGeometry args={[2.3, 0.9, 4.5]} />
      <T.MeshStandardMaterial color="#e2e8f0" metalness={0.8} roughness={0.2} />
    </T.Mesh>
    <!-- Car Cabin / Glass Roof -->
    <T.Mesh position={[0, 1.25, -0.2]}>
      <T.BoxGeometry args={[2.1, 0.75, 2.6]} />
      <T.MeshPhysicalMaterial color="#0f172a" transmission={0.7} transparent opacity={0.9} roughness={0.1} />
    </T.Mesh>
    <!-- Headlights -->
    <T.Mesh position={[-0.85, 0.65, 2.26]}>
      <T.BoxGeometry args={[0.45, 0.18, 0.05]} />
      <T.MeshBasicMaterial color="#ffffff" />
    </T.Mesh>
    <T.Mesh position={[0.85, 0.65, 2.26]}>
      <T.BoxGeometry args={[0.45, 0.18, 0.05]} />
      <T.MeshBasicMaterial color="#ffffff" />
    </T.Mesh>
    <!-- Wheels -->
    {#each [-1.15, 1.15] as wx}
      {#each [1.3, -1.3] as wz}
        <T.Mesh position={[wx, 0.35, wz]} rotation={[0, 0, Math.PI / 2]}>
          <T.CylinderGeometry args={[0.35, 0.35, 0.25, 16]} />
          <T.MeshStandardMaterial color="#0f172a" roughness={0.9} />
        </T.Mesh>
      {/each}
    {/each}
  </T.Group>


  <!-- ---------------- 2. FIRST FLOOR / MIDDLE LEVEL (Y:4.2 to Y:8.5) ---------------- -->

  <!-- Main Suite Volume (Horizontal Wood Slat Cladding) -->
  {#if woodSlatMap}
    <T.Mesh position={[-3.5, 6.35, 0.5]} castShadow receiveShadow>
      <T.BoxGeometry args={[10.5, 4.3, 8.5]} />
      <T.MeshStandardMaterial map={woodSlatMap} roughness={0.5} />
    </T.Mesh>
  {/if}

  <!-- Master Suite Large Front Picture Window -->
  <T.Mesh position={[-4.0, 6.3, 4.78]}>
    <T.BoxGeometry args={[5.2, 2.8, 0.1]} />
    <T.MeshPhysicalMaterial
      color="#0f172a"
      transmission={0.8}
      transparent
      opacity={0.85}
      roughness={0.05}
    />
  </T.Mesh>
  <T.Mesh position={[-4.0, 6.3, 4.84]}>
    <T.BoxGeometry args={[5.3, 2.9, 0.05]} />
    <T.MeshStandardMaterial color="#f8fafc" roughness={0.2} />
  </T.Mesh>

  <!-- PROMINENT CANTILEVERED WHITE BALCONY SLAB (Extending Forward) -->
  <T.Group position={[0.5, 5.8, 4.8]}>
    <!-- Thick Floating White Slab -->
    <T.Mesh castShadow>
      <T.BoxGeometry args={[11.5, 0.5, 5.5]} />
      <T.MeshStandardMaterial color="#ffffff" roughness={0.2} />
    </T.Mesh>

    <!-- Glass Balustrade Safety Railing -->
    <T.Mesh position={[0, 0.75, 2.65]}>
      <T.BoxGeometry args={[11.4, 1.0, 0.08]} />
      <T.MeshPhysicalMaterial color="#bae6fd" transmission={0.85} transparent opacity={0.6} roughness={0.1} />
    </T.Mesh>
    <!-- Stainless Handrail Tube -->
    <T.Mesh position={[0, 1.3, 2.65]}>
      <T.BoxGeometry args={[11.5, 0.08, 0.1]} />
      <T.MeshStandardMaterial color="#cbd5e1" metalness={0.9} roughness={0.1} />
    </T.Mesh>

    <!-- Balcony Green Planter Bed along the Edge -->
    <T.Mesh position={[-1.5, 0.35, 1.5]}>
      <T.BoxGeometry args={[6.5, 0.25, 1.2]} />
      <T.MeshStandardMaterial color="#365314" roughness={0.8} />
    </T.Mesh>

    <!-- Stepped Decorative White Feature Wall on Left Balcony -->
    <T.Mesh position={[-5.2, 0.8, 1.2]}>
      <T.BoxGeometry args={[0.4, 1.2, 3.2]} />
      <T.MeshStandardMaterial color="#ffffff" roughness={0.2} />
    </T.Mesh>
  </T.Group>


  <!-- ---------------- 3. TOP LEVEL / PENTHOUSE & PERGOLA (Y:8.5 to Y:12.5) ---------------- -->

  <!-- Top Penthouse Rendered Box (Beige / Taupe Concrete) -->
  <T.Mesh position={[0, 10.3, -0.5]} castShadow>
    <T.BoxGeometry args={[13.5, 3.6, 7.5]} />
    <T.MeshStandardMaterial color="#d1c7bd" roughness={0.6} />
  </T.Mesh>

  <!-- Large White Floating Roof Frame Overhang -->
  <T.Mesh position={[-0.5, 12.3, 0.5]} castShadow>
    <T.BoxGeometry args={[15.0, 0.45, 9.5]} />
    <T.MeshStandardMaterial color="#ffffff" roughness={0.2} />
  </T.Mesh>

  <!-- Decorative White Perforated Lattice Screen (Right Side Wall) -->
  {#if latticeMap}
    <T.Mesh position={[6.78, 9.8, 1.2]}>
      <T.BoxGeometry args={[0.1, 4.4, 4.5]} />
      <T.MeshStandardMaterial map={latticeMap} roughness={0.3} />
    </T.Mesh>
  {/if}

  <!-- Wooden Pergola Beams (Right Sun Deck Canopy) -->
  <T.Group position={[5.2, 10.8, 2.5]}>
    {#each [-2.2, -1.1, 0, 1.1, 2.2] as px}
      <T.Mesh position={[px, 0, 0]} castShadow>
        <T.BoxGeometry args={[0.2, 0.35, 4.5]} />
        <T.MeshStandardMaterial color="#663214" roughness={0.4} />
      </T.Mesh>
    {/each}
  </T.Group>

  <!-- Cascading Green Ivy Vines / Foliage on Pergola & Balconies -->
  <T.Mesh position={[5.2, 9.8, 4.6]}>
    <T.DodecahedronGeometry args={[0.9, 1]} />
    <T.MeshStandardMaterial color="#4d7c0f" roughness={0.8} />
  </T.Mesh>
  <T.Mesh position={[5.8, 9.0, 4.7]}>
    <T.DodecahedronGeometry args={[0.7, 1]} />
    <T.MeshStandardMaterial color="#65a30d" roughness={0.8} />
  </T.Mesh>

</T.Group>


<!-- ================= LANDSCAPING TREES & POTTED PLANTS ================= -->

<!-- Background & Side Lush Trees -->
<T.Group position={[-16, 0, -8]}>
  <T.Mesh position={[0, 4, 0]}>
    <T.CylinderGeometry args={[0.4, 0.6, 8, 8]} />
    <T.MeshStandardMaterial color="#3b1c09" roughness={0.9} />
  </T.Mesh>
  <T.Mesh position={[0, 9, 0]}>
    <T.DodecahedronGeometry args={[3.8, 1]} />
    <T.MeshStandardMaterial color="#3f6212" roughness={0.7} />
  </T.Mesh>
  <T.Mesh position={[0, 11.5, 0]}>
    <T.DodecahedronGeometry args={[2.8, 1]} />
    <T.MeshStandardMaterial color="#65a30d" roughness={0.7} />
  </T.Mesh>
</T.Group>

<T.Group position={[18, 0, -6]}>
  <T.Mesh position={[0, 4.5, 0]}>
    <T.CylinderGeometry args={[0.45, 0.65, 9, 8]} />
    <T.MeshStandardMaterial color="#3b1c09" roughness={0.9} />
  </T.Mesh>
  <T.Mesh position={[0, 10, 0]}>
    <T.DodecahedronGeometry args={[4.2, 1]} />
    <T.MeshStandardMaterial color="#3f6212" roughness={0.7} />
  </T.Mesh>
  <T.Mesh position={[0, 13, 0]}>
    <T.DodecahedronGeometry args={[3.0, 1]} />
    <T.MeshStandardMaterial color="#65a30d" roughness={0.7} />
  </T.Mesh>
</T.Group>

<!-- Potted Plants Near Carport & Entrance -->
{#each [1.8, 2.6, 3.4] as px}
  <T.Group position={[px, 0, 5.2]}>
    <T.Mesh position={[0, 0.35, 0]}>
      <T.CylinderGeometry args={[0.25, 0.2, 0.7, 12]} />
      <T.MeshStandardMaterial color="#e2e8f0" roughness={0.3} />
    </T.Mesh>
    <T.Mesh position={[0, 0.9, 0]}>
      <T.DodecahedronGeometry args={[0.35, 1]} />
      <T.MeshStandardMaterial color="#4d7c0f" roughness={0.8} />
    </T.Mesh>
  </T.Group>
{/each}


<!-- ================= INTERACTIVE 3D FLOATING HOTSPOT BADGES ================= -->
{#each villaHotspots as spot}
  <HTML position={spot.pos} center distanceFactor={35}>
    <div 
      class="villa-badge"
      class:active={activeHover === spot.id}
      style="--badge-accent: {spot.color};"
      onmouseenter={() => handleHotspotHover(spot.id)}
      onmouseleave={() => handleHotspotHover(null)}
      role="tooltip"
    >
      <div class="badge-ring"></div>
      <div class="badge-info">
        <span class="badge-title">{spot.title}</span>
        <span class="badge-desc">{spot.sub}</span>
      </div>
    </div>
  </HTML>
{/each}


<!-- ================= CAMERA & CINEMATIC PERSPECTIVE ================= -->
<T.PerspectiveCamera
  makeDefault
  position={[32, 14, 22]}
  fov={42}
>
  <OrbitControls
    target={[-6, 5, 1]}
    enableZoom={true}
    enablePan={true}
    autoRotate
    autoRotateSpeed={0.3}
    maxPolarAngle={Math.PI / 2 - 0.01}
    minPolarAngle={Math.PI / 12}
  />
</T.PerspectiveCamera>

<style>
  :global(.villa-badge) {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-left: 4px solid var(--badge-accent);
    padding: 6px 12px;
    border-radius: 8px;
    color: #ffffff;
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 11px;
    white-space: nowrap;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4), 0 0 15px var(--badge-accent);
    transition: all 0.25 ease;
    pointer-events: auto;
  }

  :global(.villa-badge:hover, .villa-badge.active) {
    transform: scale(1.1) translateY(-3px);
    background: rgba(15, 23, 42, 0.95);
    border-color: var(--badge-accent);
  }

  :global(.badge-ring) {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--badge-accent);
    box-shadow: 0 0 10px var(--badge-accent);
    animation: ringPulse 1.6s infinite ease-in-out;
  }

  :global(.badge-info) {
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  :global(.badge-title) {
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.5px;
    color: #ffffff;
  }

  :global(.badge-desc) {
    font-size: 9px;
    color: #94a3b8;
  }

  @keyframes ringPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(0.8); }
  }
</style>
