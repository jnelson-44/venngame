(() => {
  const canvas = document.getElementById('stage');
  const ctx = canvas.getContext('2d');

  const off = document.createElement('canvas');
  off.width = canvas.width;
  off.height = canvas.height;
  const octx = off.getContext('2d');

  const R = 140;
  const A = { x: 320, y: 315, r: R, name: 'A' };
  const B = { x: 480, y: 315, r: R, name: 'B' };
  const C = { x: 400, y: 200, r: R, name: 'C' };

  const statusMessage = document.getElementById('statusMessage');
  const timerEl = document.getElementById('timer');

  const startOverlay = document.getElementById('startOverlay');
  const startBtn = document.getElementById('startBtn');
  const tutorialBtn = document.getElementById('tutorialBtn');

  const tutorialOverlay = document.getElementById('tutorialOverlay');
  const tutorialTitle = document.getElementById('tutorialTitle');
  const tutorialText = document.getElementById('tutorialText');
  const tutorialBack = document.getElementById('tutorialBack');
  const tutorialNext = document.getElementById('tutorialNext');
  const tutorialDots = document.querySelectorAll('#tutorialDots .dot');
  const tutorialExit = document.getElementById('tutorialExit');

  const completeOverlay = document.getElementById('completeOverlay');
  const completeTime = document.getElementById('completeTime');
  const completeClose = document.getElementById('completeClose');
  const shareResults = document.getElementById('shareResults');

  const averageTimeValue = document.getElementById('averageTimeValue');
  const playersSolvedValue = document.getElementById('playersSolvedValue');
  const currentStreakValue = document.getElementById('currentStreakValue');
  const bestStreakValue = document.getElementById('bestStreakValue');

  const mobileStatsBtn = document.getElementById('mobileStatsBtn');
  const mobileStatsOverlay = document.getElementById('mobileStatsOverlay');
  const mobileStatsClose = document.getElementById('mobileStatsClose');
  const mobileAverageTimeValue = document.getElementById('mobileAverageTimeValue');
  const mobilePlayersSolvedValue = document.getElementById('mobilePlayersSolvedValue');
  const mobileCurrentStreakValue = document.getElementById('mobileCurrentStreakValue');
  const mobileBestStreakValue = document.getElementById('mobileBestStreakValue');

  const wordInput = document.getElementById('wordInput');
  const submitWordBtn = document.getElementById('submitWordBtn');
  const entryBar = document.getElementById('entryBar');
  const entryStatus = document.getElementById('entryStatus');
  const hint = document.querySelector('.hint');

  let gameStarted = false;
  let tutorialMode = false;
  let timerInterval = null;
  let startTime = null;
  let finalShareTime = "0:00";
  let puzzleCompleted = false;

  let regionTextPositions = {};

  let labelA = "A";
  let labelB = "B";
  let labelC = "C";

  let puzzleData = null;
  let validWords = null;

  let tutorialStep = 0;
  let flashingMask = 0;
  let flashStartTime = 0;
  const flashDuration = 400;

  let lastMask = 0;
  let clickedMask = 0;
  let hoveredMask = 0;
  let clickedMaskTimeout = null;


  let dictionary = null;

  const notes = {};

  const tutorialLabels = {
    A: "Contains the letter V",
    B: "At least 8 letters",
    C: "Starts with S"
  };

  const tutorialSteps = [
    {
      title: "Welcome",
      text: "Each circle represents a rule. Words belong in the region where all the rules apply.",
      highlight: null
    },
    {
      title: "Single Rules",
      text: "Words in outer regions satisfy only one rule.",
      highlight: 1
    },
    {
      title: "Two Rules",
      text: "Overlapping regions must satisfy both rules.",
      highlight: 3
    },
    {
      title: "Three Rules",
      text: "The center region must satisfy all three rules.",
      highlight: 7
    },
    {
      title: "Enter Words",
      text: "Type a word into the text box and press enter. If it is valid, it will automatically be placed in the correct region.",
      highlight: null
    },
    {
      title: "You're Ready",
      text: "Fill every region with a valid word to complete the puzzle.",
      highlight: null
    }
  ];

  function setStatus(message, color) {
    statusMessage.textContent = message;
    statusMessage.style.color = color;

    if (entryStatus) {
      entryStatus.textContent = message;
      entryStatus.style.color = color;
    }
  }

  function syncMobileStats() {
    if (mobileAverageTimeValue && averageTimeValue) {
      mobileAverageTimeValue.textContent = averageTimeValue.textContent;
    }
    if (mobilePlayersSolvedValue && playersSolvedValue) {
      mobilePlayersSolvedValue.textContent = playersSolvedValue.textContent;
    }
    if (mobileCurrentStreakValue && currentStreakValue) {
      mobileCurrentStreakValue.textContent = currentStreakValue.textContent;
    }
    if (mobileBestStreakValue && bestStreakValue) {
      mobileBestStreakValue.textContent = bestStreakValue.textContent;
    }
  }

  function pointIn(c, x, y) {
    const dx = x - c.x;
    const dy = y - c.y;
    return (dx * dx + dy * dy) <= c.r * c.r;
  }

  function pointInMask(mask, x, y) {
    const inA = pointIn(A, x, y);
    const inB = pointIn(B, x, y);
    const inC = pointIn(C, x, y);
    const actualMask = (inA ? 1 : 0) | (inB ? 2 : 0) | (inC ? 4 : 0);
    return actualMask === mask;
  }

  function regionAt(x, y) {
    const inA = pointIn(A, x, y) ? 1 : 0;
    const inB = pointIn(B, x, y) ? 2 : 0;
    const inC = pointIn(C, x, y) ? 4 : 0;
    return inA | inB | inC;
  }

  function computeRegionCenter(mask, step = 4) {
    let sumX = 0;
    let sumY = 0;
    let count = 0;

    for (let y = 0; y < canvas.height; y += step) {
      for (let x = 0; x < canvas.width; x += step) {
        if (pointInMask(mask, x, y)) {
          sumX += x;
          sumY += y;
          count++;
        }
      }
    }

    if (count === 0) return null;

    return {
      x: sumX / count,
      y: sumY / count
    };
  }

  function drawCircleOutline(c, stroke) {
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  function fillCircle(c) {
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawRegion(mask, color = 'rgba(0,0,0,0.16)') {
    octx.clearRect(0, 0, off.width, off.height);

    const inc = [];
    if (mask & 1) inc.push(A);
    if (mask & 2) inc.push(B);
    if (mask & 4) inc.push(C);

    const exc = [];
    if (!(mask & 1)) exc.push(A);
    if (!(mask & 2)) exc.push(B);
    if (!(mask & 4)) exc.push(C);

    if (inc.length === 0) return;

    octx.globalCompositeOperation = 'source-over';
    octx.fillStyle = '#000';
    octx.beginPath();
    octx.arc(inc[0].x, inc[0].y, inc[0].r, 0, Math.PI * 2);
    octx.fill();

    for (let i = 1; i < inc.length; i++) {
      octx.globalCompositeOperation = 'destination-in';
      octx.beginPath();
      octx.arc(inc[i].x, inc[i].y, inc[i].r, 0, Math.PI * 2);
      octx.fill();
    }

    for (const c of exc) {
      octx.globalCompositeOperation = 'destination-out';
      octx.beginPath();
      octx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
      octx.fill();
    }

    octx.globalCompositeOperation = 'source-in';
    octx.fillStyle = color;
    octx.fillRect(0, 0, off.width, off.height);

    ctx.globalCompositeOperation = 'source-over';
    ctx.drawImage(off, 0, 0);
  }

  function drawWrappedLabel(text, x, y, {
    maxWidth = 180,
    lineHeight = window.innerWidth < 760 ? 20 : 18,
    align = 'center',
    font = window.innerWidth < 760
  ? 'bold 24px system-ui, -apple-system, Segoe UI, Roboto, sans-serif'
  : 'bold 16px system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
    color = '#333',
    glow = false
  } = {}) {
    ctx.save();
    ctx.font = font;
    ctx.fillStyle = color;
    ctx.textAlign = align;

    if (glow) {
      ctx.shadowColor = 'rgba(255, 152, 0, 0.9)';
      ctx.shadowBlur = 16;
    } else {
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
    }

    const paragraphs = String(text).split('\n');
const lines = [];

for (const paragraph of paragraphs) {
  const words = paragraph.split(/\s+/);
  let line = "";

  for (let i = 0; i < words.length; i++) {
    const test = line ? line + " " + words[i] : words[i];
    if (ctx.measureText(test).width <= maxWidth) {
      line = test;
    } else {
      if (line) lines.push(line);

      if (ctx.measureText(words[i]).width > maxWidth) {
        let chunk = "";
        for (const ch of words[i]) {
          if (ctx.measureText(chunk + ch).width <= maxWidth) {
            chunk += ch;
          } else {
            lines.push(chunk);
            chunk = ch;
          }
        }
        line = chunk;
      } else {
        line = words[i];
      }
    }
  }

  if (line) lines.push(line);
}

    const totalHeight = lines.length * lineHeight;
    let yStart = y - totalHeight / 2 + lineHeight * 0.85;

    for (const ln of lines) {
      ctx.fillText(ln, x, yStart);
      yStart += lineHeight;
    }

    ctx.restore();
  }

  function drawRegionWord(mask, word) {
    const pos = regionTextPositions[mask];
    if (!pos) return;

    const maxWidths = {
      1: 150,
      2: 150,
      3: 120,
      4: 170,
      5: 120,
      6: 120,
      7: 105
    };

    const maxWidth = maxWidths[mask] || 120;
    let fontSize = 18;
    const minFontSize = 10;

    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#000";

    while (fontSize >= minFontSize) {
      ctx.font = `bold ${fontSize}px system-ui, -apple-system, Segoe UI, Roboto, sans-serif`;
      if (ctx.measureText(word).width <= maxWidth) {
        break;
      }
      fontSize--;
    }

    ctx.fillText(word, pos.x, pos.y);
    ctx.restore();
  }

  function getFlashAlpha() {
    if (!flashingMask || !flashStartTime) return null;

    const elapsed = Date.now() - flashStartTime;

    if (elapsed >= flashDuration) {
      flashingMask = 0;
      flashStartTime = 0;
      return null;
    }

    if (elapsed <= 200) {
      const t = elapsed / 200;
      return 0.28 + (0.60 - 0.28) * t;
    }

    const t = (elapsed - 200) / 200;
    return 0.60 + (0.28 - 0.60) * t;
  }

  function drawBase() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawCircleOutline(A, '#000');
    drawCircleOutline(B, '#000');
    drawCircleOutline(C, '#000');

    ctx.globalAlpha = 0.05;
    ctx.fillStyle = '#000';
    fillCircle(A);
    fillCircle(B);
    fillCircle(C);
    ctx.globalAlpha = 1;

    if (gameStarted || tutorialMode) {
      const isMobile = window.innerWidth < 760;
const activeMask = isMobile ? clickedMask : (hoveredMask || clickedMask);

drawWrappedLabel(
  window.innerWidth < 760 ? splitSideRule(labelA, 16) : labelA,
  window.innerWidth < 760 ? 95 : A.x - A.r - 24,
  A.y,
  {
    maxWidth: window.innerWidth < 760 ? 170 : 200,
    align: window.innerWidth < 760 ? 'center' : 'right',
    glow: !!(activeMask & 1),
    color: (activeMask & 1) ? '#111' : '#333'
  }
);

drawWrappedLabel(
  window.innerWidth < 760 ? splitSideRule(labelB, 16) : labelB,
  window.innerWidth < 760 ? 705 : B.x + B.r + 24,
  B.y,
  {
    maxWidth: window.innerWidth < 760 ? 170 : 200,
    align: window.innerWidth < 760 ? 'center' : 'left',
    glow: !!(activeMask & 2),
    color: (activeMask & 2) ? '#111' : '#333'
  }
);

drawWrappedLabel(labelC, C.x, C.y - C.r - 28, {
  maxWidth: window.innerWidth < 760 ? 320 : 220,
  align: 'center',
  glow: !!(activeMask & 4),
  color: (activeMask & 4) ? '#111' : '#333'
});
    }

    const flashAlpha = getFlashAlpha();

    const isMobile = window.innerWidth < 760;

for (let mask = 1; mask <= 7; mask++) {
  if (notes[mask]) {
    if (mask === flashingMask && flashAlpha !== null) {
      drawRegion(mask, `rgba(0,0,0,${flashAlpha})`);
    } else {
      drawRegion(mask, 'rgba(0,0,0,0.28)');
    }
  } else if (isMobile && mask === clickedMask) {
    drawRegion(mask, 'rgba(0,0,0,0.16)');
  } else if (!isMobile && mask === hoveredMask) {
    drawRegion(mask, 'rgba(0,0,0,0.16)');
  }
}

    for (const [key, word] of Object.entries(notes)) {
      drawRegionWord(Number(key), word);
    }
  }

  function formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  }

  function formatSeconds(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  }

  function startTimer() {
    startTime = Date.now();
    timerEl.textContent = "0:00";
    timerEl.style.visibility = "visible";

    timerInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      timerEl.textContent = formatTime(elapsed);
    }, 250);
  }

  function allRegionsFilled() {
    for (let mask = 1; mask <= 7; mask++) {
      if (!notes[mask]) return false;
    }
    return true;
  }

  function animateInputError() {
    if (wordInput?.animate) {
      wordInput.animate(
        [
          { transform: 'translateX(0)' },
          { transform: 'translateX(-8px)' },
          { transform: 'translateX(8px)' },
          { transform: 'translateX(-6px)' },
          { transform: 'translateX(6px)' },
          { transform: 'translateX(0)' }
        ],
        { duration: 280, easing: 'ease' }
      );
    }

    if (entryBar?.animate) {
      entryBar.animate(
        [
          { transform: 'translateX(0)' },
          { transform: 'translateX(-4px)' },
          { transform: 'translateX(4px)' },
          { transform: 'translateX(0)' }
        ],
        { duration: 280, easing: 'ease' }
      );
    }
  }

  function wordBelongsInRegion(word, mask) {
    if (!validWords) return false;
    const regionList = validWords[String(mask)] || [];
    return regionList.includes(word);
  }

  function findRegionForWord(word) {
    if (!validWords) return 0;

    for (let mask = 1; mask <= 7; mask++) {
      const regionList = validWords[String(mask)] || [];
      if (regionList.includes(word)) {
        return mask;
      }
    }

    return 0;
  }

  function flashRegion(mask) {
    flashingMask = mask;
    flashStartTime = Date.now();

    function animateFlash() {
      drawBase();

      if (flashingMask) {
        requestAnimationFrame(animateFlash);
      } else if (allRegionsFilled()) {
        completePuzzle();
      }
    }

    requestAnimationFrame(animateFlash);
  }

  async function completePuzzle() {
    if (puzzleCompleted) return;
    puzzleCompleted = true;

    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }

    const elapsedMs = Date.now() - startTime;
    const solveTimeSeconds = Math.floor(elapsedMs / 1000);
    finalShareTime = formatTime(elapsedMs);

    completeTime.textContent = `Your time: ${finalShareTime}`;
    completeOverlay.style.display = "flex";

    updateStreakOnSolve();

    if (!puzzleData?.id) return;

    try {
      const response = await fetch("/api/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          puzzleId: puzzleData.id,
          solveTimeSeconds
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadStats();
    } catch (err) {
      console.error("Failed to submit solve:", err);
    }
  }

  function submitWord() {
    if (!gameStarted || tutorialMode || puzzleCompleted) return;

    const word = wordInput.value.trim().toLowerCase();

    if (!word) {
      statusMessage.textContent = "Enter a word first.";
      statusMessage.style.color = "#c62828";
      animateInputError();
      return;
    }

    if (!puzzleData || !validWords) {
      statusMessage.textContent = "Puzzle data not loaded.";
      statusMessage.style.color = "#c62828";
      animateInputError();
      return;
    }

    // check dictionary first
if (!dictionary || !dictionary.has(word)) {
  statusMessage.textContent = "That word is not in the dictionary.";
  statusMessage.style.color = "#c62828";
  animateInputError();
  return;
}

const mask = findRegionForWord(word);

if (!mask) {
  statusMessage.textContent = "That word doesn't belong in any region.";
  statusMessage.style.color = "#c62828";
  animateInputError();
  return;
}

    if (notes[mask]) {
      statusMessage.textContent = "That section is already filled.";
      statusMessage.style.color = "#c62828";
      animateInputError();
      return;
    }

    notes[mask] = word;
    wordInput.value = "";
    lastMask = mask;

    statusMessage.textContent = "Valid word";
    statusMessage.style.color = "#2e7d32";

    flashRegion(mask);
    wordInput.focus();
  }

  async function loadStats() {
    if (!puzzleData?.id) return;

    try {
      const response = await fetch(`/api/stats/${encodeURIComponent(puzzleData.id)}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const stats = await response.json();

      playersSolvedValue.textContent = String(stats.playersSolved || 0);
      averageTimeValue.textContent =
        stats.averageTime > 0 ? formatSeconds(stats.averageTime) : "--:--";

      syncMobileStats();
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  }

  function getTodayLocalString() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function getYesterdayLocalString() {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function getStreakData() {
    const raw = localStorage.getItem('intersection_streak');
    if (!raw) {
      return {
        currentStreak: 0,
        bestStreak: 0,
        lastSolvedDate: null
      };
    }

    try {
      const parsed = JSON.parse(raw);
      return {
        currentStreak: Number(parsed.currentStreak) || 0,
        bestStreak: Number(parsed.bestStreak) || 0,
        lastSolvedDate: parsed.lastSolvedDate || null
      };
    } catch {
      return {
        currentStreak: 0,
        bestStreak: 0,
        lastSolvedDate: null
      };
    }
  }

  function saveStreakData(data) {
    localStorage.setItem('intersection_streak', JSON.stringify(data));
  }

  function renderStreak() {
    const data = getStreakData();
    currentStreakValue.textContent = String(data.currentStreak);
    bestStreakValue.textContent = String(data.bestStreak);
    syncMobileStats();
  }

  function updateStreakOnSolve() {
    const today = getTodayLocalString();
    const yesterday = getYesterdayLocalString();
    const data = getStreakData();

    if (data.lastSolvedDate === today) {
      renderStreak();
      return;
    }

    if (data.lastSolvedDate === yesterday) {
      data.currentStreak += 1;
    } else {
      data.currentStreak = 1;
    }

    if (data.currentStreak > data.bestStreak) {
      data.bestStreak = data.currentStreak;
    }

    data.lastSolvedDate = today;
    saveStreakData(data);
    renderStreak();
  }

  async function loadPuzzleData() {
    try {
      const response = await fetch('/api/puzzle');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      puzzleData = await response.json();
validWords = puzzleData.regions;

// load dictionary
const dictResponse = await fetch('/dictionary.txt');
const dictText = await dictResponse.text();
dictionary = new Set(
  dictText
    .split('\n')
    .map(w => w.trim().toLowerCase())
    .filter(Boolean)
);

      if (puzzleData.labels) {
        labelA = puzzleData.labels.A || labelA;
        labelB = puzzleData.labels.B || labelB;
        labelC = puzzleData.labels.C || labelC;
      }

      regionTextPositions = {};
      for (let mask = 1; mask <= 7; mask++) {
        const center = computeRegionCenter(mask, 3);
        if (center) {
          regionTextPositions[mask] = center;
        }
      }

      drawBase();
      renderStreak();
      await loadStats();
    } catch (err) {
      console.error("Failed to load puzzleData.json:", err);
      alert("Could not load puzzleData.json");
    }
  }

  function renderTutorialStep() {
    const step = tutorialSteps[tutorialStep];

    tutorialTitle.textContent = step.title;
    tutorialText.textContent = step.text;

    tutorialDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === tutorialStep);
    });

    tutorialBack.style.visibility = tutorialStep === 0 ? 'hidden' : 'visible';
    tutorialNext.textContent =
      tutorialStep === tutorialSteps.length - 1 ? "Done" : "Next";

    drawBase();

    if (step.highlight) {
      drawRegion(step.highlight, 'rgba(0,0,0,0.25)');
    }
  }

  canvas.addEventListener('click', (e) => {
  if (!gameStarted || tutorialMode) return;

  const rect = canvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) * (canvas.width / rect.width);
  const y = (e.clientY - rect.top) * (canvas.height / rect.height);

  const mask = regionAt(x, y);
if (!mask) return;

  const isMobile = window.innerWidth < 760;

lastMask = mask;

const rules = [];
if (mask & 1) rules.push(labelA);
if (mask & 2) rules.push(labelB);
if (mask & 4) rules.push(labelC);

setStatus(
  "Must satisfy: " + rules.join(" • "),
  "#444"
);

if (isMobile) {
  clickedMask = mask;

  if (clickedMaskTimeout) {
    clearTimeout(clickedMaskTimeout);
  }

  clickedMaskTimeout = setTimeout(() => {
    clickedMask = 0;
    clickedMaskTimeout = null;
    setStatus("", "");
    drawBase();
  }, 5000);
}

drawBase();
});

  startBtn.addEventListener('click', () => {
    tutorialMode = false;
    gameStarted = true;
    startOverlay.style.display = 'none';
    canvas.classList.remove('prestart');
    entryBar.style.display = 'block';
    if (hint) hint.style.display = 'block';
    startTimer();
    drawBase();
    wordInput.focus();
  });

  tutorialBtn.addEventListener('click', () => {
    tutorialStep = 0;
    tutorialMode = true;

    labelA = tutorialLabels.A;
    labelB = tutorialLabels.B;
    labelC = tutorialLabels.C;

    startOverlay.style.display = 'none';
    tutorialOverlay.style.display = 'flex';

    drawBase();
    renderTutorialStep();
  });

  tutorialBack.addEventListener('click', () => {
    if (tutorialStep > 0) {
      tutorialStep--;
      renderTutorialStep();
    }
  });

  tutorialNext.addEventListener('click', () => {
    if (tutorialStep < tutorialSteps.length - 1) {
      tutorialStep++;
      renderTutorialStep();
      return;
    }

    tutorialOverlay.style.display = 'none';
    tutorialMode = false;
    clickedMask = 0;

    if (puzzleData?.labels) {
      labelA = puzzleData.labels.A;
      labelB = puzzleData.labels.B;
      labelC = puzzleData.labels.C;
    }

    drawBase();
    startOverlay.style.display = 'flex';
  });

  tutorialExit.addEventListener('click', () => {
    tutorialOverlay.style.display = 'none';
    tutorialMode = false;
    clickedMask = 0;

    if (puzzleData?.labels) {
      labelA = puzzleData.labels.A;
      labelB = puzzleData.labels.B;
      labelC = puzzleData.labels.C;
    }

    drawBase();
    startOverlay.style.display = 'flex';
  });

  submitWordBtn.addEventListener('click', submitWord);

  wordInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      submitWord();
    }
  });

  completeClose.addEventListener('click', () => {
    completeOverlay.style.display = "none";
  });

  shareResults.addEventListener('click', async () => {
    const shareText = `I finished today’s Intersection puzzle in ${finalShareTime}. Can you beat my time?

https://venngame-ncza.onrender.com/`;

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(shareText);
      } else {
        const temp = document.createElement("textarea");
        temp.value = shareText;
        temp.style.position = "fixed";
        temp.style.opacity = "0";
        temp.style.pointerEvents = "none";
        document.body.appendChild(temp);
        temp.focus();
        temp.select();

        const successful = document.execCommand("copy");
        document.body.removeChild(temp);

        if (!successful) {
          throw new Error("Fallback copy failed");
        }
      }


      completeTime.innerHTML = "<strong>Copied</strong><br>Thanks for playing!";
    } catch (err) {
      console.error("Clipboard copy failed:", err);
      completeTime.innerHTML =
        "<strong>Copy failed</strong><br>Your browser blocked clipboard access on this page.";
    }
  });

  if (mobileStatsBtn) {
    mobileStatsBtn.addEventListener('click', () => {
      syncMobileStats();
      mobileStatsOverlay.classList.add('open');
    });
  }

  if (mobileStatsClose) {
    mobileStatsClose.addEventListener('click', () => {
      mobileStatsOverlay.classList.remove('open');
    });
  }

  if (mobileStatsOverlay) {
    mobileStatsOverlay.addEventListener('click', (e) => {
      if (e.target === mobileStatsOverlay) {
        mobileStatsOverlay.classList.remove('open');
      }
    });
  }

  addEventListener('resize', () => {
    drawBase();
    if (lastMask && !notes[lastMask] && gameStarted && !tutorialMode) {
      drawRegion(lastMask);
    }
  });


const stageEl = document.getElementById('stage');

function adjustForKeyboard() {
  if (!window.visualViewport || !stageEl) return;
  if (document.activeElement !== wordInput) return;

  const keyboardHeight = window.innerHeight - window.visualViewport.height;
  const keyboardOpen = keyboardHeight > 120;

  if (!keyboardOpen) return;

  setTimeout(() => {
    const rect = stageEl.getBoundingClientRect();
    const targetTop = 90;
    const targetBottom = window.visualViewport.height - 24;

    if (rect.bottom > targetBottom || rect.top < targetTop) {
      const absoluteTop = window.scrollY + rect.top;
      const desiredScroll =
        absoluteTop - targetTop - Math.max(0, (window.visualViewport.height - rect.height) / 2);

      window.scrollTo({
        top: Math.max(0, desiredScroll),
        behavior: 'smooth'
      });
    }
  }, 120);
}

canvas.addEventListener('mousemove', (e) => {
  if (!gameStarted || tutorialMode) return;
  if (window.innerWidth < 760) return;

  const rect = canvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) * (canvas.width / rect.width);
  const y = (e.clientY - rect.top) * (canvas.height / rect.height);

  const mask = regionAt(x, y);
  hoveredMask = mask;

  if (!clickedMask) {
    if (mask) {
      const rules = [];
      if (mask & 1) rules.push(labelA);
      if (mask & 2) rules.push(labelB);
      if (mask & 4) rules.push(labelC);

      setStatus("Must satisfy: " + rules.join(" • "), "#444");
    } else {
      setStatus("", "");
    }
  }

  drawBase();
});

function splitSideRule(text, maxChars = 16) {
  const str = String(text).trim();
  if (str.length <= maxChars) return str;

  const words = str.split(/\s+/);
  if (words.length < 2) return str;

  let bestIndex = 1;
  let bestDiff = Infinity;

  for (let i = 1; i < words.length; i++) {
    const left = words.slice(0, i).join(' ');
    const right = words.slice(i).join(' ');
    const diff = Math.abs(left.length - right.length);

    if (diff < bestDiff) {
      bestDiff = diff;
      bestIndex = i;
    }
  }

  return words.slice(0, bestIndex).join(' ') + '\n' +
         words.slice(bestIndex).join(' ');
}

canvas.addEventListener('mouseleave', () => {
  if (window.innerWidth < 760) return;

  hoveredMask = 0;

  if (!clickedMask) {
    setStatus("", "");
  }

  drawBase();
});

if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', adjustForKeyboard);
}

wordInput.addEventListener('focus', adjustForKeyboard);
wordInput.addEventListener('click', adjustForKeyboard);

  drawBase();
  loadPuzzleData();
})();