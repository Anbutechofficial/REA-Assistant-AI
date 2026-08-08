<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    LayoutDashboard, 
    History, 
    Mic, 
    Database, 
    HelpCircle, 
    ChevronLeft, 
    ChevronRight, 
    Sun, 
    Moon, 
    Settings, 
    User, 
    Paperclip, 
    Sparkles, 
    Send, 
    CloudUpload, 
    CheckCircle2, 
    AlertCircle, 
    X, 
    Activity,
    FileText,
    Copy,
    Check,
    ArrowUpRight,
    Search,
    Building2
  } from '@lucide/svelte';

  // --- STATE VARIABLES ---
  
  // Navigation & Theme
  let sidebarCollapsed = $state(false);
  let activeSidebarTab = $state('Dashboard'); // 'Dashboard', 'Query History', 'Audio Transcripts', 'Data Sources', 'Help Center'
  let isLightTheme = $state(false);

  // Backend Interaction
  let quickAskQuestion = $state('');
  let isAsking = $state(false);
  let isTranscribing = $state(false);
  
  let textareaRef = $state<HTMLTextAreaElement | null>(null);

  $effect(() => {
    if (quickAskQuestion !== undefined && textareaRef) {
      textareaRef.style.height = 'auto';
      textareaRef.style.height = Math.min(textareaRef.scrollHeight, 180) + 'px';
    }
  });
  
  // Audio recording state
  let isRecording = $state(false);
  let mediaStream = $state<MediaStream | null>(null);
  let mediaRecorder = $state<MediaRecorder | null>(null);
  let audioChunks: Blob[] = [];

  // System Status
  let apiConnected = $state(false);
  let statusBannerText = $state('Checking system connection...');
  let lastUpdatedTime = $state('Never');

  // Conversation logs
  interface ChatMessage {
    sender: 'user' | 'ai';
    name: string;
    time: string;
    text: string;
    bulletPoints?: Array<{ label: string; value: string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
    showChart?: boolean;
    summary?: string;
  }

  let messages = $state<ChatMessage[]>([]);

  // General History / Saved Items
  interface HistoryItem {
    question: string;
    answer: string;
    time: string;
  }
  let queryHistory = $state<HistoryItem[]>([]);

  interface TranscriptItem {
    filename: string;
    size: string;
    text: string;
    time: string;
  }
  let audioTranscripts = $state<TranscriptItem[]>([]);

  // Clipboard Copied indicators
  let copiedIndex = $state<number | null>(null);

  // Chat Feed Scrolling
  let conversationFeedRef = $state<HTMLDivElement | null>(null);

  function scrollToBottom() {
    if (conversationFeedRef) {
      setTimeout(() => {
        conversationFeedRef!.scrollTo({
          top: conversationFeedRef!.scrollHeight,
          behavior: 'smooth'
        });
      }, 50);
    }
  }

  $effect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  });

  // --- COMPONENT MOUNT ---
  onMount(() => {
    // Sync theme with document class list (defaulting to dark mode)
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      isLightTheme = true;
      document.documentElement.classList.add('light-theme');
    } else {
      isLightTheme = false;
      document.documentElement.classList.remove('light-theme');
    }

    // Initial backend check and start interval
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 8000);
    return () => clearInterval(interval);
  });

  // --- ACTIONS ---

  // Theme Toggler
  function toggleTheme() {
    isLightTheme = !isLightTheme;
    if (isLightTheme) {
      document.documentElement.classList.add('light-theme');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.remove('light-theme');
      localStorage.setItem('theme', 'dark');
    }
  }

  // Health check polling
  async function checkBackendHealth() {
    try {
      const res = await fetch('http://localhost:8000/');
      if (res.ok) {
        apiConnected = true;
        statusBannerText = 'All systems operational';
      } else {
        apiConnected = false;
        statusBannerText = 'Backend server returned error status';
      }
    } catch (e) {
      apiConnected = false;
      statusBannerText = 'Connection failed: Ensure FastAPI is running on port 8000';
    }
    const d = new Date();
    lastUpdatedTime = d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  // Send RAG Search Query
  async function sendQuestion(questionText: string) {
    if (!questionText.trim() || isAsking) return;
    
    const currentQuestion = questionText;
    quickAskQuestion = '';
    isAsking = true;
    
    // Add user message immediately
    const userTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messages.push({
      sender: 'user',
      name: 'You',
      time: 'Today, ' + userTime,
      text: currentQuestion
    });

    // Create a temporary loading message from AI
    messages.push({
      sender: 'ai',
      name: 'AI Assistant',
      time: 'Today, ' + userTime,
      text: 'Retrieving vector listings and generating answers...'
    });

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: currentQuestion })
      });

      if (!response.ok) {
        throw new Error('API server returned error status ' + response.status);
      }

      const data = await response.json();
      
      // Remove loading message
      messages.pop();

      // Check if it's a trend question to show chart
      const isTrend = currentQuestion.toLowerCase().includes('trend') || 
                      currentQuestion.toLowerCase().includes('price') || 
                      currentQuestion.toLowerCase().includes('market');

      // Parse answer text for lines or bullet points
      const rawAnswer = data.answer || "I couldn't find a suitable property based on the available data.";
      
      // Separate basic response
      messages.push({
        sender: 'ai',
        name: 'AI Assistant',
        time: 'Today, ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: rawAnswer,
        showChart: isTrend
      });

      // Save to general history
      queryHistory.push({
        question: currentQuestion,
        answer: rawAnswer,
        time: new Date().toLocaleString()
      });

    } catch (err: any) {
      messages.pop(); // Remove loading
      messages.push({
        sender: 'ai',
        name: 'AI Assistant',
        time: 'Today, ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `Error: Unable to complete request. Details: ${err.message}. Please verify the FastAPI backend is running.`
      });
    } finally {
      isAsking = false;
      checkBackendHealth();
    }
  }

  // Voice Recording & Transcription via Web Audio API
  async function toggleRecording() {
    if (isRecording) {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      isRecording = false;
    } else {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(mediaStream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const file = new File([audioBlob], 'voice-input.webm', { type: 'audio/webm' });
          
          if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
          }

          await transcribeAudioBlob(file);
        };

        mediaRecorder.start();
        isRecording = true;
      } catch (err) {
        alert('Microphone access denied or unavailable. Please enable mic permissions.');
        console.error(err);
      }
    }
  }

  async function transcribeAudioBlob(file: File) {
    isTranscribing = true;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error('Transcription API returned error status ' + res.status);
      }

      const data = await res.json();
      const transcribedText = data.text || '';

      if (transcribedText.trim()) {
        quickAskQuestion = (quickAskQuestion ? quickAskQuestion + ' ' : '') + transcribedText;
        
        audioTranscripts.push({
          filename: 'Voice Search Record',
          size: (file.size / (1024 * 1024)).toFixed(2) + 'MB',
          text: transcribedText,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      }
    } catch (err: any) {
      alert(`Voice Search Transcription Failed: ${err.message}. Ensure GROQ_API_KEY is active.`);
    } finally {
      isTranscribing = false;
      checkBackendHealth();
    }
  }

  function copyToClipboard(text: string, index: number) {
    navigator.clipboard.writeText(text);
    copiedIndex = index;
    setTimeout(() => {
      if (copiedIndex === index) copiedIndex = null;
    }, 2000);
  }

  // Re-ask from query history
  function reloadQuery(question: string) {
    quickAskQuestion = question;
    activeSidebarTab = 'Dashboard';
  }
</script>

<div class="dashboard-container">
  
  <!-- SIDEBAR NAVIGATION -->
  <aside class="sidebar" class:collapsed={sidebarCollapsed}>
    <div class="sidebar-top">
      <div class="logo-box">
        <a href="/" class="home-logo-btn" title="Back to Landing Page">
          <Building2 size={22} class="home-svg-icon" />
        </a>
        {#if !sidebarCollapsed}
          <div class="logo-text">
            <h2>REA Assistant AI</h2>
            <span class="logo-ver">v0.1.0</span>
          </div>
        {/if}
      </div>

      <nav class="sidebar-menu">
        <button 
          class="menu-item" 
          class:active={activeSidebarTab === 'Dashboard'} 
          onclick={() => activeSidebarTab = 'Dashboard'}
          title="Dashboard"
        >
          <LayoutDashboard size={20} />
          {#if !sidebarCollapsed}<span>Dashboard</span>{/if}
        </button>

        <button 
          class="menu-item" 
          class:active={activeSidebarTab === 'Query History'} 
          onclick={() => activeSidebarTab = 'Query History'}
          title="Query History"
        >
          <History size={20} />
          {#if !sidebarCollapsed}
            <span>Query History</span>
            <span class="count-badge">{queryHistory.length}</span>
          {/if}
        </button>
      </nav>
    </div>

    <!-- Collapse Toggle button at bottom -->
    <button class="collapse-btn" onclick={() => sidebarCollapsed = !sidebarCollapsed}>
      {#if sidebarCollapsed}
        <ChevronRight size={18} />
      {:else}
        <ChevronLeft size={18} />
        <span>Collapse</span>
      {/if}
    </button>
  </aside>

  <!-- MAIN WORKSPACE -->
  <div class="workspace">
    
    <!-- TOP HEADER -->
    <header class="workspace-header">
      <div class="header-left">
        <h1>{activeSidebarTab}</h1>
      </div>
      
      <div class="header-right">
        <!-- Theme Toggle -->
        <button class="icon-btn" onclick={toggleTheme} title="Toggle Theme">
          {#if isLightTheme}
            <Moon size={20} />
          {:else}
            <Sun size={20} />
          {/if}
        </button>
        
        <!-- Settings -->
        <button class="icon-btn" title="Settings" onclick={() => alert('Settings Modal: Backend URL: http://localhost:8000')}>
          <Settings size={20} />
        </button>

        <div class="divider"></div>

        <!-- User Profile Dropdown -->
        <div class="user-profile">
          <div class="avatar">
            <User size={18} color="#ffffff" />
          </div>
          <span class="username">Admin User</span>
        </div>
      </div>
    </header>

    <!-- VIEWS CONTROLLER BASED ON TAB -->
    <main class="workspace-content">
      
      {#if activeSidebarTab === 'Dashboard'}
        <div class="dashboard-grid">
            <!-- CONVERSATION HISTORY LOGS -->
            <section class="glass-panel card-box conversation-card">
              <div class="card-header">
                <div class="title-with-icon">
                  <svg class="header-blue-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M8 12h8"/>
                    <path d="M12 8v8"/>
                  </svg>
                  <h3>Conversation</h3>
                </div>
              </div>

              <div class="conversation-feed" bind:this={conversationFeedRef}>
                {#if messages.length === 0}
                  <div class="empty-conversation animate-fade-in">
                    <div class="empty-convo-icon">
                      <Building2 size={32} color="#060913" />
                    </div>
                    <h4>Your Conversation Starts Here</h4>
                    <p>Ask a question about property values, market trends, or listings to begin RAG retrieval analysis.</p>
                    <div class="empty-convo-suggestions">
                      <button onclick={() => quickAskQuestion = "What is the current market trend for 3-bedroom homes in Austin, TX?"}>
                        "What is the market trend in Austin, TX?"
                      </button>
                      <button onclick={() => quickAskQuestion = "Are there any listings at 123 Main St?"}>
                        "Are there any listings at 123 Main St?"
                      </button>
                    </div>
                  </div>
                {:else}
                  {#each messages as msg, i}
                    <div class="chat-bubble-container" class:user-bubble={msg.sender === 'user'}>
                      <div class="bubble-header">
                        <div class="bubble-avatar" style="background-color: {msg.sender === 'user' ? '#59FF00' : '#4cd600'};">
                          {#if msg.sender === 'user'}
                            <User size={14} color="#060913" />
                          {:else}
                            <Building2 size={14} color="#060913" />
                          {/if}
                        </div>
                        <span class="bubble-sender">{msg.name}</span>
                        <span class="bubble-time">{msg.time}</span>
                      </div>

                      <div class="bubble-text">
                        <p>{msg.text}</p>
                        
                        <!-- Render Bullet Stats for initial Austin Trend response -->
                        {#if msg.bulletPoints}
                          <ul class="bullet-list">
                            {#each msg.bulletPoints as bp}
                              <li>
                                <span class="bullet-label">{bp.label}:</span>
                                <strong class="bullet-val">{bp.value}</strong>
                                {#if bp.change}
                                  <span class="bullet-change" class:positive={bp.changeType === 'positive'} class:neutral={bp.changeType === 'neutral'}>
                                    ({bp.change})
                                  </span>
                                {/if}
                              </li>
                            {/each}
                          </ul>
                        {/if}

                        <!-- Render SVG Chart for Austin Market Trend -->
                        {#if msg.showChart}
                          <div class="chart-container glass-panel">
                            <div class="chart-header-row">
                              <h5>Median Price Trend (3-Bedroom Homes)</h5>
                            </div>
                            
                            <!-- Custom SVG Chart matching mock layout -->
                            <div class="svg-wrapper">
                              <svg width="100%" height="150" viewBox="0 0 520 150" preserveAspectRatio="none">
                                <defs>
                                  <linearGradient id="chartGlow" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stop-color="#59FF00" stop-opacity="0.3"/>
                                    <stop offset="100%" stop-color="#59FF00" stop-opacity="0.0"/>
                                  </linearGradient>
                                </defs>
                                
                                <!-- Y Axis Reference Lines -->
                                <line x1="60" y1="20" x2="500" y2="20" stroke="var(--border-light)" stroke-dasharray="3,3" />
                                <line x1="60" y1="60" x2="500" y2="60" stroke="var(--border-light)" stroke-dasharray="3,3" />
                                <line x1="60" y1="100" x2="500" y2="100" stroke="var(--border-light)" stroke-dasharray="3,3" />
                                <line x1="60" y1="130" x2="500" y2="130" stroke="var(--border-light)" />
                                
                                <!-- Y Labels -->
                                <text x="15" y="24" fill="var(--text-muted)" font-size="10" font-family="Inter">$600K</text>
                                <text x="15" y="64" fill="var(--text-muted)" font-size="10" font-family="Inter">$500K</text>
                                <text x="15" y="104" fill="var(--text-muted)" font-size="10" font-family="Inter">$400K</text>
                                <text x="15" y="134" fill="var(--text-muted)" font-size="10" font-family="Inter">$300K</text>
                                
                                <!-- Chart filled area -->
                                <path d="M 60 120 L 130 110 L 200 95 L 270 82 L 340 70 L 410 55 L 480 38 L 480 130 L 60 130 Z" fill="url(#chartGlow)" />
                                
                                <!-- Line Plot -->
                                <path d="M 60 120 L 130 110 L 200 95 L 270 82 L 340 70 L 410 55 L 480 38" fill="none" stroke="#59FF00" stroke-width="2.5" />
                                
                                <!-- Data points (circles) -->
                                <circle cx="60" cy="120" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="130" cy="110" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="200" cy="95" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="270" cy="82" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="340" cy="70" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="410" cy="55" r="4" fill="#ffffff" stroke="#59FF00" stroke-width="2" />
                                <circle cx="480" cy="38" r="4" fill="#59FF00" stroke="#ffffff" stroke-width="2" />

                                <!-- X Labels -->
                                <text x="45" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Jul '23</text>
                                <text x="115" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Sep '23</text>
                                <text x="185" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Nov '23</text>
                                <text x="255" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Jan '24</text>
                                <text x="325" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Mar '24</text>
                                <text x="395" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">May '24</text>
                                <text x="465" y="146" fill="var(--text-muted)" font-size="9" font-family="Inter">Jul '24</text>
                              </svg>
                            </div>
                          </div>
                        {/if}

                        {#if msg.summary}
                          <p class="summary-text">{msg.summary}</p>
                        {/if}
                      </div>
                    </div>
                  {/each}
                {/if}
              </div>
            </section>

            <!-- QUICK ASK CARD -->
            <section class="glass-panel card-box quick-ask-card">
              <div class="card-header">
                <div class="title-with-icon">
                  <svg class="header-blue-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  <h3>Quick Ask</h3>
                </div>
              </div>

              <div class="quick-ask-body">
                <textarea 
                  bind:this={textareaRef}
                  placeholder="Ask in English or Tanglish (e.g., '3 BHK in Egmore' or 'Egmore la 3 BHK budget 50 lakhs irukka')."
                  bind:value={quickAskQuestion}
                  disabled={isAsking}
                  onkeydown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendQuestion(quickAskQuestion);
                    }
                  }}
                ></textarea>
                
                <div class="quick-ask-footer">
                   <div class="voice-lang-badge">🎙️ English & Tanglish Supported</div>
                   <div class="action-buttons-group">
                      <button 
                        class="btn-primary voice-btn" 
                        class:recording={isRecording}
                        class:transcribing={isTranscribing}
                        title={isRecording ? "Stop Recording" : isTranscribing ? "Transcribing..." : "Voice Search (English & Tanglish Supported)"} 
                        onclick={toggleRecording}
                        disabled={isAsking}
                        type="button"
                      >
                        {#if isTranscribing}
                          <span class="mini-spinner"></span>
                        {:else}
                          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke={isRecording ? "#ef4444" : "#060913"} stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="mic-svg">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                            <line x1="12" y1="19" x2="12" y2="22"/>
                          </svg>
                        {/if}
                      </button>
                     
                     <button 
                       class="btn-primary send-btn" 
                       onclick={() => sendQuestion(quickAskQuestion)}
                       disabled={isAsking || !quickAskQuestion.trim()}
                     >
                       {#if isAsking}
                         <span class="spinner"></span>
                         <span>Processing...</span>
                       {:else}
                         <Send size={16} />
                         <span>Send Question</span>
                       {/if}
                     </button>
                   </div>
                 </div>
              </div>
            </section>
        </div>
      
      {:else}
        
        <!-- OTHER NAVIGATION VIEWS -->
        <div class="other-view-container glass-panel animate-fade-in">
          
          {#if activeSidebarTab === 'Query History'}
            <div class="history-view">
              <h3>Saved Ask Sessions</h3>
              <p class="section-subtitle">A collection of questions posed to the vector retrieval engine.</p>
              
              {#if queryHistory.length === 0}
                <div class="empty-state">
                  <History size={48} class="text-muted" />
                  <p>No queries recorded in this session yet.</p>
                </div>
              {:else}
                <div class="history-list">
                  {#each queryHistory as item, index}
                    <div class="history-item-row">
                      <div class="history-meta">
                        <span class="history-time">{item.time}</span>
                        <button class="reload-btn" onclick={() => reloadQuery(item.question)}>
                          Run Again <ArrowUpRight size={14} />
                        </button>
                      </div>
                      <div class="history-content">
                        <strong>Q: {item.question}</strong>
                        <p>A: {item.answer.substring(0, 150)}...</p>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

          {/if}
          
        </div>
      {/if}

    </main>
  </div>

</div>

<style>
  /* --- LAYOUT GRID --- */
  .dashboard-container {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background-color: var(--bg-primary);
  }

  /* --- SIDEBAR --- */
  .sidebar {
    width: 250px;
    height: 100%;
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border-light);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.5rem 1rem;
    transition: width var(--transition-normal);
    z-index: 10;
    flex-shrink: 0;
  }

  .sidebar.collapsed {
    width: 72px;
    padding: 1.5rem 0.6rem;
  }

  .sidebar-top {
    display: flex;
    flex-direction: column;
    gap: 2.2rem;
  }

  .logo-box {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-left: 0.5rem;
  }

  .home-logo-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-primary);
    color: #ffffff;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    transition: background-color var(--transition-fast);
    flex-shrink: 0;
  }

  .home-logo-btn:hover {
    background-color: var(--color-primary-hover);
  }

  .home-svg-icon {
    width: 18px;
    height: 18px;
  }

  .logo-text h2 {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
  }

  .logo-ver {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-family: var(--font-body);
  }

  .sidebar-menu {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    background: none;
    border: none;
    padding: 10px 14px;
    border-radius: 8px;
    color: var(--text-secondary);
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    text-align: left;
    width: 100%;
    transition: background-color var(--transition-fast), color var(--transition-fast);
  }

  .menu-item:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
  }

  .light-theme .menu-item:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .menu-item.active {
    background-color: var(--color-primary);
    color: #ffffff;
  }

  .count-badge {
    margin-left: auto;
    font-size: 0.75rem;
    background: rgba(255, 255, 255, 0.15);
    color: var(--text-primary);
    padding: 1px 6px;
    border-radius: 10px;
    font-weight: 600;
  }

  .green-badge {
    background-color: var(--color-success-bg);
    color: var(--color-success);
  }

  .collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 0.85rem;
    font-family: var(--font-display);
    font-weight: 500;
    padding: 10px;
    cursor: pointer;
    border-radius: 8px;
    transition: color var(--transition-fast), background-color var(--transition-fast);
  }

  .collapse-btn:hover {
    color: var(--text-primary);
    background-color: rgba(255, 255, 255, 0.04);
  }

  /* --- WORKSPACE --- */
  .workspace {
    flex-grow: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-primary);
    overflow: hidden;
  }

  /* --- HEADER --- */
  .workspace-header {
    height: 64px;
    border-bottom: 1px solid var(--border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    background-color: var(--bg-secondary);
    flex-shrink: 0;
  }

  .workspace-header h1 {
    font-size: 1.25rem;
    color: var(--text-primary);
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .icon-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color var(--transition-fast), color var(--transition-fast);
  }

  .icon-btn:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
  }

  .light-theme .icon-btn:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .divider {
    width: 1px;
    height: 24px;
    background-color: var(--border-light);
    margin: 0 0.5rem;
  }

  .user-profile {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .username {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  /* --- WORKSPACE CONTENT --- */
  .workspace-content {
    flex-grow: 1;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* --- DASHBOARD GRID --- */
  .dashboard-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    flex-grow: 1;
    overflow: hidden;
  }

  .conversation-card {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .quick-ask-card {
    flex-shrink: 0;
  }

  /* --- CARDS --- */
  .card-box {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border-light);
  }

  .title-with-icon {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .header-blue-icon {
    color: var(--color-accent);
  }

  .card-header h3 {
    font-size: 1.05rem;
    color: var(--text-primary);
  }

  .api-tag {
    font-family: monospace;
    font-size: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border-light);
    margin-left: 6px;
  }

  .light-theme .api-tag {
    background: rgba(0, 0, 0, 0.03);
  }

  /* --- QUICK ASK BOX --- */
  .quick-ask-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .quick-ask-body textarea {
    width: 100%;
    height: 48px;
    min-height: 48px;
    max-height: 180px;
    background-color: rgba(0, 0, 0, 0.12);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 12px;
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 0.92rem;
    line-height: 1.5;
    resize: none;
    outline: none;
    transition: border-color var(--transition-fast), background-color var(--transition-fast);
    overflow-y: auto;
  }

  .light-theme .quick-ask-body textarea {
    background-color: #ffffff;
  }

  .quick-ask-body textarea:focus {
    border-color: var(--color-accent);
  }

  .quick-ask-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .editor-tools {
    display: flex;
    gap: 0.5rem;
  }

  .action-buttons-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .tool-btn {
    background: none;
    border: 1px solid var(--border-light);
    color: var(--text-secondary);
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color var(--transition-fast), color var(--transition-fast);
  }

  .voice-btn {
    width: 44px;
    height: 44px;
    min-width: 44px;
    padding: 0;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-primary, #59FF00) !important;
    border: none !important;
    color: #060913 !important;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(89, 255, 0, 0.25);
    flex-shrink: 0;
  }

  .voice-btn:hover {
    background-color: var(--color-primary-hover, #4cd600) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(89, 255, 0, 0.35);
  }

  .voice-btn .mic-svg {
    stroke: #060913 !important;
    display: block;
  }

  .voice-btn.recording .mic-svg {
    stroke: #ef4444 !important;
  }

  .voice-lang-badge {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--color-accent);
    background: rgba(89, 255, 0, 0.08);
    border: 1px solid rgba(89, 255, 0, 0.2);
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
  }

  .tool-btn:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
  }

  .light-theme .tool-btn:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .send-btn {
    min-width: 150px;
  }

  /* --- CONVERSATION FEED --- */
  .conversation-feed {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    flex-grow: 1;
    overflow-y: auto;
  }

  .chat-bubble-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 82%;
    align-self: flex-start;
  }

  .chat-bubble-container.user-bubble {
    align-self: flex-end;
  }

  .chat-bubble-container.user-bubble .bubble-header {
    flex-direction: row-reverse;
  }

  .chat-bubble-container.user-bubble .bubble-text {
    background-color: rgba(89, 255, 0, 0.1);
    border-color: rgba(89, 255, 0, 0.25);
    border-top-right-radius: 2px;
  }

  .light-theme .chat-bubble-container.user-bubble .bubble-text {
    background-color: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.25);
  }

  .chat-bubble-container:not(.user-bubble) .bubble-text {
    border-top-left-radius: 2px;
  }

  .bubble-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .bubble-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .bubble-sender {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .bubble-time {
    font-size: 0.75rem;
    color: var(--text-muted);
  }

  .bubble-text {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 1rem;
    font-size: 0.92rem;
    line-height: 1.5;
    color: var(--text-primary);
    white-space: pre-wrap;
  }

  .light-theme .bubble-text {
    background-color: #f8fafc;
  }

  .bullet-list {
    margin: 1rem 0 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .bullet-label {
    color: var(--text-secondary);
  }

  .bullet-val {
    color: var(--text-primary);
    margin-left: 4px;
  }

  .bullet-change {
    font-size: 0.8rem;
    margin-left: 6px;
  }

  .bullet-change.positive {
    color: var(--color-success);
  }

  .bullet-change.neutral {
    color: var(--text-muted);
  }

  .summary-text {
    margin-top: 1rem;
    border-top: 1px solid var(--border-light);
    padding-top: 0.8rem;
    color: var(--text-secondary);
  }

  /* --- SVG CHART --- */
  .chart-container {
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 12px;
  }

  .chart-header-row h5 {
    font-size: 0.85rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
  }

  .svg-wrapper {
    width: 100%;
    margin-top: 0.5rem;
  }

  /* --- VOICE INTERFACE --- */
  .voice-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .dropzone {
    border: 2px dashed rgba(59, 130, 246, 0.35);
    background: rgba(59, 130, 246, 0.02);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: background-color var(--transition-fast), border-color var(--transition-fast);
    outline: none;
  }

  .dropzone:hover, .dropzone.dragover {
    background-color: rgba(59, 130, 246, 0.06);
    border-color: var(--color-accent);
  }

  .upload-icon {
    color: var(--color-accent);
    margin-bottom: 0.75rem;
  }

  .drop-text {
    font-size: 0.85rem;
    color: var(--text-primary);
    font-weight: 500;
  }

  .sub-text {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .hidden-file-input {
    display: none;
  }

  .selected-file-card {
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .light-theme .selected-file-card {
    background-color: #ffffff;
  }

  .file-details {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    overflow: hidden;
  }

  .file-name {
    color: var(--text-primary);
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 140px;
  }

  .file-size {
    color: var(--text-muted);
  }

  .clear-file-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .clear-file-btn:hover {
    color: #ef4444;
  }

  .transcribe-btn {
    width: 100%;
  }

  /* Audio Waves Loader Animation */
  .audio-waves-loader {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 18px;
  }

  .audio-waves-loader span {
    width: 3px;
    height: 100%;
    background-color: #ffffff;
    border-radius: 3px;
    animation: bounce 0.8s infinite ease-in-out;
  }

  .audio-waves-loader span:nth-child(2) { animation-delay: 0.15s; }
  .audio-waves-loader span:nth-child(3) { animation-delay: 0.3s; }
  .audio-waves-loader span:nth-child(4) { animation-delay: 0.45s; }

  @keyframes bounce {
    0%, 100% { transform: scaleY(0.3); }
    50% { transform: scaleY(1); }
  }

  /* --- SYSTEM STATUS --- */
  .status-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 0.75rem;
    font-size: 0.88rem;
  }

  .status-row:last-of-type {
    border-bottom: none;
    padding-bottom: 0;
  }

  .status-label {
    color: var(--text-secondary);
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .led {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
  }

  .led.green {
    background-color: var(--color-success);
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  }

  .led.red {
    background-color: #ef4444;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
  }

  .text-right {
    text-align: right;
  }

  .status-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.82rem;
    margin-top: 0.5rem;
    font-weight: 500;
  }

  .success-banner {
    background-color: var(--color-success-bg);
    color: var(--color-success);
    border: 1px solid rgba(16, 185, 129, 0.2);
  }

  .error-banner {
    background-color: rgba(239, 68, 68, 0.1);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  .banner-icon {
    flex-shrink: 0;
  }

  /* --- OTHER PAGES CONTAINER --- */
  .other-view-container {
    padding: 2rem;
    flex-grow: 1;
    overflow-y: auto;
  }

  .section-subtitle {
    font-size: 0.88rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
    gap: 1rem;
    font-size: 0.95rem;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .history-item-row {
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 1.25rem;
  }

  .history-item-row:last-child {
    border-bottom: none;
  }

  .history-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }

  .history-time {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .reload-btn {
    background: none;
    border: 1px solid var(--border-light);
    color: var(--color-accent);
    font-size: 0.78rem;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: background-color var(--transition-fast);
  }

  .reload-btn:hover {
    background-color: rgba(89, 255, 0, 0.08);
  }

  .history-content strong {
    font-size: 0.95rem;
    color: var(--text-primary);
    display: block;
    margin-bottom: 4px;
  }

  .history-content p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .transcript-quote {
    font-size: 0.9rem;
    font-style: italic;
    color: var(--text-secondary);
    border-left: 3px solid var(--border-light);
    padding-left: 10px;
    margin-top: 6px;
  }

  /* --- DATA SOURCE LISTINGS --- */
  .listings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .listing-item-card {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .listing-header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
  }

  .listing-header-main h4 {
    font-size: 0.95rem;
    color: var(--text-primary);
  }

  .price-tag {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.9rem;
    color: var(--color-accent);
  }

  .listing-desc {
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .listing-badges {
    display: flex;
    gap: 8px;
    margin-top: auto;
  }

  .listing-badges span {
    font-size: 0.75rem;
    background-color: rgba(255, 255, 255, 0.04);
    color: var(--text-muted);
    border: 1px solid var(--border-light);
    padding: 2px 6px;
    border-radius: 4px;
  }

  .light-theme .listing-badges span {
    background-color: #f1f5f9;
  }

  .vector-store-stats {
    padding: 1.5rem;
  }

  .vector-store-stats h5 {
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
  }

  .vector-store-stats ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.88rem;
  }

  .vector-store-stats li strong {
    color: var(--text-primary);
  }

  /* --- HELP SECTION --- */
  .faq-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .faq-item h5 {
    font-size: 0.95rem;
    color: var(--text-primary);
    margin-bottom: 6px;
  }

  .faq-item p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .code-block {
    background-color: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--border-light);
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin-top: 6px;
  }

  .light-theme .code-block {
    background-color: #f8fafc;
  }

  .code-block code {
    font-family: monospace;
    font-size: 0.82rem;
    color: var(--color-accent);
  }

  /* --- UTILITY SPINNER --- */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-top: 2px solid #ffffff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .tool-btn.voice-btn.recording {
    background-color: rgba(239, 68, 68, 0.15);
    border-color: #ef4444;
    animation: micPulse 1.5s infinite ease-in-out;
  }
  
  @keyframes micPulse {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }
    50% {
      box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
  }

  .mini-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(89, 255, 0, 0.25);
    border-top: 2px solid var(--color-accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .empty-conversation {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 1.5rem;
    text-align: center;
    color: var(--text-muted);
  }

  .empty-convo-icon {
    background: rgba(89, 255, 0, 0.1);
    color: var(--color-accent);
    padding: 1rem;
    border-radius: 50%;
    margin-bottom: 1.25rem;
  }

  .empty-conversation h4 {
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-size: 1.15rem;
  }

  .empty-conversation p {
    font-size: 0.88rem;
    max-width: 440px;
    line-height: 1.5;
    margin-bottom: 1.75rem;
  }

  .empty-convo-suggestions {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    align-items: center;
    width: 100%;
    max-width: 340px;
  }

  .empty-convo-suggestions button {
    width: 100%;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-family: var(--font-body);
    cursor: pointer;
    text-align: left;
    transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
  }

  .light-theme .empty-convo-suggestions button {
    background: #ffffff;
  }

  .empty-convo-suggestions button:hover {
    background: rgba(89, 255, 0, 0.05);
    border-color: var(--color-accent);
    color: var(--color-accent);
  }
</style>
