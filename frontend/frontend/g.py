from IPython.display import HTML

HTML('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ox Alpha — AI Resume Checker</title>
<style>
  :root {
    --bg: #0f1117; --card: #1a1d27; --card2: #222636;
    --accent: #6c5ce7; --accent2: #00cec9;
    --green: #00b894; --red: #e17055; --text: #e9eaf0; --muted: #8a8fa3;
  }
  * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',system-ui,sans-serif; }
  body { background:var(--bg); color:var(--text); min-height:100vh; padding:24px; }
  .container { max-width:1100px; margin:0 auto; }
  header { text-align:center; margin-bottom:32px; }
  header h1 { font-size:2rem; background:linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip:text; background-clip:text; color:transparent; }
  header p { color:var(--muted); margin-top:6px; }

  .grid { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
  @media(max-width:860px){ .grid{grid-template-columns:1fr;} }
  .card { background:var(--card); border:1px solid #2a2e40; border-radius:16px; padding:24px; }

  /* Upload zone */
  .dropzone {
    border:2px dashed #3a3f55; border-radius:14px; padding:40px 20px;
    text-align:center; cursor:pointer; transition:all .25s;
  }
  .dropzone:hover, .dropzone.dragover { border-color:var(--accent); background:rgba(108,92,231,.08); }
  .dropzone .icon { font-size:2.4rem; }
  .dropzone h3 { margin:10px 0 4px; }
  .dropzone p { color:var(--muted); font-size:.85rem; }
  .file-chip {
    display:none; margin-top:14px; background:var(--card2); padding:10px 16px;
    border-radius:20px; font-size:.9rem; align-items:center; gap:8px;
  }
  .file-chip.show { display:inline-flex; }
  .file-chip button { background:none; border:none; color:var(--red); cursor:pointer; font-size:1rem; }

  textarea {
    width:100%; min-height:180px; background:var(--card2); color:var(--text);
    border:1px solid #2a2e40; border-radius:12px; padding:14px; resize:vertical;
    font-size:.92rem; line-height:1.5; outline:none;
  }
  textarea:focus { border-color:var(--accent); }

  .analyze-btn {
    width:100%; margin-top:16px; padding:14px; border:none; border-radius:12px;
    background:linear-gradient(90deg,var(--accent),var(--accent2)); color:#fff;
    font-size:1rem; font-weight:600; cursor:pointer; transition:transform .15s, opacity .2s;
  }
  .analyze-btn:hover { transform:translateY(-2px); }
  .analyze-btn:disabled { opacity:.5; cursor:not-allowed; transform:none; }

  .live-badge {
    display:inline-flex; align-items:center; gap:6px; font-size:.75rem;
    color:var(--muted); margin-top:8px;
  }
  .live-dot { width:8px; height:8px; border-radius:50%; background:var(--muted); }
  .live-dot.active { background:var(--green); animation:pulse 1s infinite; }
  @keyframes pulse { 50%{opacity:.4;} }

  /* Results */
  #results { display:none; margin-top:24px; }
  .results-grid { display:grid; grid-template-columns:300px 1fr; gap:24px; }
  @media(max-width:860px){ .results-grid{grid-template-columns:1fr;} }

  .score-wrap { display:flex; flex-direction:column; align-items:center; gap:12px; }
  .circle { position:relative; width:180px; height:180px; }
  .circle svg { transform:rotate(-90deg); }
  .circle .track { fill:none; stroke:#2a2e40; stroke-width:12; }
  .circle .bar {
    fill:none; stroke:url(#grad); stroke-width:12; stroke-linecap:round;
    stroke-dasharray:502; stroke-dashoffset:502;
    transition:stroke-dashoffset 1.2s cubic-bezier(.25,.8,.25,1);
  }
  .score-num { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
  .score-num span:first-child { font-size:2.6rem; font-weight:700; }
  .score-num span:last-child { color:var(--muted); font-size:.8rem; }

  .ats-meter { width:100%; }
  .meter-bar { height:10px; background:#2a2e40; border-radius:6px; overflow:hidden; }
  .meter-fill { height:100%; width:0; border-radius:6px; background:linear-gradient(90deg,var(--red),var(--accent2)); transition:width 1s ease; }
  .meter-labels { display:flex; justify-content:space-between; font-size:.75rem; color:var(--muted); margin-top:6px; }

  h2.section { font-size:1.05rem; margin-bottom:14px; color:var(--accent2); }
  .keyword-cloud { display:flex; flex-wrap:wrap; gap:8px; }
  .kw { padding:6px 12px; border-radius:20px; font-size:.82rem; animation:pop .3s ease both; }
  @keyframes pop { from{transform:scale(.6); opacity:0;} }
  .kw.match { background:rgba(0,184,148,.15); color:#55efc4; border:1px solid rgba(0,184,148,.4); }
  .kw.missing { background:rgba(225,112,85,.12); color:#fab1a0; border:1px solid rgba(225,112,85,.4); }

  ul.suggestions { list-style:none; }
  ul.suggestions li {
    background:var(--card2); border-left:3px solid var(--accent); border-radius:8px;
    padding:12px 14px; margin-bottom:10px; font-size:.88rem; line-height:1.5;
    animation:slideIn .4s ease both;
  }
  @keyframes slideIn { from{transform:translateX(-14px); opacity:0;} }
  .loading { display:none; text-align:center; padding:10px; color:var(--muted); }
  .spinner { display:inline-block; width:22px; height:22px; border:3px solid #2a2e40; border-top-color:var(--accent); border-radius:50%; animation:spin .7s linear infinite; }
  @keyframes spin { to{transform:rotate(360deg);} }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>AI Resume Checker</h1>
    <p>Upload your resume, paste the job description, get an instant ATS match analysis.</p>
  </header>

  <div class="grid">
    <!-- LEFT: inputs -->
    <div class="card">
      <div class="dropzone" id="dropzone">
        <div class="icon">📄</div>
        <h3>Drag & drop your resume</h3>
        <p>or click to browse — PDF, DOCX, TXT (max 5MB)</p>
        <div class="file-chip" id="fileChip">
          <span id="fileName"></span>
          <button id="removeFile" title="Remove">✕</button>
        </div>
      </div>
      <input type="file" id="fileInput" hidden accept=".pdf,.doc,.docx,.txt">

      <h2 class="section" style="margin-top:22px;">Job Description</h2>
      <textarea id="jobDesc" placeholder="Paste the full job description here..."></textarea>
      <div class="live-badge"><span class="live-dot" id="liveDot"></span> Live analysis active — score updates as you type</div>

      <button class="analyze-btn" id="analyzeBtn" disabled>🔍 Analyze Resume</button>
      <div class="loading" id="loading"><span class="spinner"></span> Analyzing your resume…</div>
    </div>

    <!-- RIGHT: results -->
    <div class="card" id="results">
      <div class="results-grid">
        <div class="score-wrap">
          <div class="circle">
            <svg width="180" height="180">
              <defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#e17055"/><stop offset="100%" stop-color="#00cec9"/>
              </linearGradient></defs>
              <circle class="track" cx="90" cy="90" r="80"/>
              <circle class="bar" id="scoreBar" cx="90" cy="90" r="80"/>
            </svg>
            <div class="score-num"><span id="scoreValue">0%</span><span>Match Score</span></div>
          </div>
          <div class="ats-meter">
            <h2 class="section" style="font-size:.85rem;">ATS Compatibility</h2>
            <div class="meter-bar"><div class="meter-fill" id="atsFill"></div></div>
            <div class="meter-labels"><span>Poor</span><span>Good</span><span>Excellent</span></div>
          </div>
        </div>

        <div>
          <h2 class="section">Keyword Gap Analysis</h2>
          <div class="keyword-cloud" id="keywordCloud"></div>
          <h2 class="section" style="margin-top:22px;">AI Suggestions</h2>
          <ul class="suggestions" id="suggestions"></ul>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileChip = document.getElementById('fileChip');
const fileNameEl = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');
const jobDesc = document.getElementById('jobDesc');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const scoreBar = document.getElementById('scoreBar');
const scoreValue = document.getElementById('scoreValue');
const atsFill = document.getElementById('atsFill');
const keywordCloud = document.getElementById('keywordCloud');
const suggestions = document.getElementById('suggestions');
const liveDot = document.getElementById('liveDot');

let uploadedFile = null, debounceTimer = null;

/* ---------- Drag & Drop ---------- */
dropzone.addEventListener('click', () => fileInput.click());
['dragover','dragenter'].forEach(e => dropzone.addEventListener(e, ev => { ev.preventDefault(); dropzone.classList.add('dragover'); }));
['dragleave','drop'].forEach(e => dropzone.addEventListener(e, ev => { ev.preventDefault(); dropzone.classList.remove('dragover'); }));
dropzone.addEventListener('drop', ev => { if (ev.dataTransfer.files.length) setFile(ev.dataTransfer.files[0]); });
fileInput.addEventListener('change', () => { if (fileInput.files.length) setFile(fileInput.files[0]); });

function setFile(f) {
  if (f.size > 5 * 1024 * 1024) return alert('File exceeds 5MB.');
  uploadedFile = f;
  fileNameEl.textContent = '📎 ' + f.name;
  fileChip.classList.add('show');
  validate();
}
removeFile.addEventListener('click', e => {
  e.stopPropagation(); uploadedFile = null; fileInput.value = '';
  fileChip.classList.remove('show'); validate();
});

jobDesc.addEventListener('input', () => { validate(); scheduleLiveAnalysis(); });

function validate() { analyzeBtn.disabled = !(uploadedFile && jobDesc.value.trim().length > 30); }

/* ---------- Analyze ---------- */
analyzeBtn.addEventListener('click', runAnalysis);

function scheduleLiveAnalysis() {
  liveDot.classList.add('active');
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => { liveDot.classList.remove('active'); if (validateReady()) runAnalysis(true); }, 1200);
}
const validateReady = () => uploadedFile && jobDesc.value.trim().length >30;

/* ---------- Mock analysis engine (replace with your real API call) ---------- */
async function runAnalysis(isLive = false) {
  if (!isLive) { loading.style.display = 'block'; analyzeBtn.disabled = true; }
  await new Promise(r => setTimeout(r, isLive ? 300 : 900)); // simulate latency

  /* ==== REPLACE THIS BLOCK WITH YOUR API ====
  const fd = new FormData();
  fd.append('resume', uploadedFile);
  fd.append('job_description', jobDesc.value);
  const res = await fetch('/api/analyze', { method: 'POST', body: fd });
  const data = await res.json();
  =========================================== */

 /* Two: upload → analyze */
const up =new FormData();
up.append('file', uploadedFile);
const upRes = await fetch('http://localhost:8000/upload-resume', { method: 'POST', body: up });
const { resume_text } = await upRes.json();

const an = new FormData();
an.append('resume_text', resume_text);
an.append('job_description', jobDesc.value);
const res = await fetch('http://localhost:8000/analyze', { method: 'POST', body: an });
const data = await res.json();

}

function mockAnalyze(text) {
  const lib = ['python','sql','react','javascript','docker','aws','communication',
    'teamwork','agile','rest api','machine learning','ci/cd','leadership','git','testing'];
  const lower = text.toLowerCase();
  const matched = lib.filter(k => lower.includes(k));
  const missing = lib.filter(k => !lower.includes(k));
  const score = Math.min(95, 30 + matched.length * 8);
  return {
    score,
    ats: Math.min(98, score + 10),
    matched,
    missing,
    suggestions: [
      'Add the missing keywords naturally into your skills section or experience bullets.',
      'Quantify achievements with numbers (e.g., "improved performance by 40%").',
      'Use standard section headers (Experience, Education, Skills) for better ATS parsing.',
      'Keep the resume to one page per 10 years of experience and avoid tables/columns.'
    ]
  };
}

/* ---------- Render ---------- */
function renderResults(data) {
  results.style.display = 'block';
  requestAnimationFrame(() => {
    const C = 2 * Math.PI * 80; // circumference ≈ 502
    scoreBar.style.strokeDashoffset = C - (data.score / 100) * C;
    scoreValue.textContent = data.score + '%';
    atsFill.style.width = data.ats_score + '%';
  });

  keywordCloud.innerHTML = '';
  data.matched_keywords.forEach((k, i) => addKeyword(k, 'match', i));
  data.missing.forEach((k, i) => addKeyword(k, 'missing', i));
  suggestions.innerHTML = data.suggestions.map(s => `<li>${s}</li>`).join('');
}

function addKeyword(k, cls, i) {
  const el = document.createElement('span');
  el.className = 'kw ' + cls;
  el.textContent = (cls === 'match' ? '✓ ' : '✕ ') + k;
  el.style.animationDelay = (i * 0.05) + 's';
  keywordCloud.appendChild(el);
}
</script>
</body>
</html>
''')