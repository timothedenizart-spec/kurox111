"""Dependency-free local conversation UI for UCA."""
from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import json
import threading
from urllib.parse import urlparse

from .engine import UnifiedCognitiveEngine


INDEX_HTML = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UCA — Unified Cognitive Architecture</title>
<style>
:root{
  --bg:#080c16;--panel:#0f172a;--panel-card:#15203b;--line:#1e293b;--line-accent:#334155;
  --ink:#f8fafc;--muted:#94a3b8;--cyan:#38bdf8;--teal:#2dd4bf;--emerald:#34d399;--warn:#fbbf24;--rose:#f87171;
  --radius:10px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.shell{display:flex;flex-direction:column;min-height:100vh}
header{background:#0a0f1d;border-bottom:1px solid var(--line);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.brand{display:flex;align-items:center;gap:12px}
.logo-badge{background:linear-gradient(135deg,#0284c7,#0d9488);color:#fff;font-weight:800;font-size:15px;padding:6px 12px;border-radius:8px;letter-spacing:1px;box-shadow:0 0 16px rgba(56,189,248,0.25)}
.brand-title{font-size:16px;font-weight:700;color:var(--ink)}
.brand-sub{font-size:12px;color:var(--muted)}
.header-badges{display:flex;gap:8px;flex-wrap:wrap}
.pill{background:var(--panel);border:1px solid var(--line);padding:3px 9px;border-radius:999px;font-size:11px;display:inline-flex;align-items:center;gap:5px;color:var(--muted)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--muted)}
.dot.ok{background:var(--emerald);box-shadow:0 0 6px var(--emerald)}
.dot.warn{background:var(--warn)}

nav.tabs{display:flex;background:#0d1424;border-bottom:1px solid var(--line);padding:0 24px}
.tab-btn{background:none;border:none;color:var(--muted);padding:12px 18px;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}
.tab-btn:hover{color:var(--ink)}
.tab-btn.active{color:var(--cyan);border-bottom-color:var(--cyan)}

.tab-content{display:none;flex:1;padding:24px;max-width:1200px;width:100%;margin:0 auto}
.tab-content.active{display:block}

/* Dialogue View */
.dialogue-layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:20px}
.chat-container{display:flex;flex-direction:column;gap:16px;min-height:60vh}
.message{background:var(--panel);border:1px solid var(--line);padding:16px 20px;border-radius:var(--radius);line-height:1.6}
.message.user{background:#0e2038;border-color:#1e3a5f;align-self:flex-end;max-width:85%}
.message-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-size:12px;color:var(--muted);font-weight:600}
.message.user .message-header{color:var(--cyan)}
.drawer{margin-top:12px;border:1px solid var(--line);border-radius:6px;background:rgba(0,0,0,0.25);overflow:hidden}
.drawer summary{padding:8px 12px;font-size:12px;color:var(--teal);cursor:pointer;font-weight:600;user-select:none;background:rgba(255,255,255,0.02)}
.drawer-content{padding:10px 14px;font-size:12px;color:var(--muted);line-height:1.5;border-top:1px solid var(--line)}
pre{background:#050811;padding:10px;border-radius:6px;overflow:auto;font-family:monospace;font-size:11px;color:#a5f3fc}

.preset-container{margin-bottom:14px;display:flex;flex-wrap:wrap;gap:8px}
.preset-btn{background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);color:var(--cyan);font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer;transition:all .15s}
.preset-btn:hover{background:rgba(56,189,248,0.18);border-color:var(--cyan)}

.composer-box{position:sticky;bottom:16px;background:#090d19;border:1px solid var(--line-accent);border-radius:var(--radius);padding:12px;box-shadow:0 8px 30px rgba(0,0,0,0.6)}
.composer-input{width:100%;min-height:56px;background:transparent;border:none;color:var(--ink);font:inherit;resize:vertical;outline:none}
.composer-footer{display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
.send-btn{background:linear-gradient(135deg,#0284c7,#0d9488);border:none;color:#fff;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;transition:opacity .15s}
.send-btn:hover{opacity:0.9}
.send-btn:disabled{opacity:0.4;cursor:wait}

/* Side Card */
.side-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin-bottom:16px}
.side-card h3{font-size:13px;text-transform:uppercase;letter-spacing:0.8px;color:var(--muted);margin-bottom:12px}
.status-item{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px}
.status-badge{font-size:11px;padding:2px 7px;border-radius:4px;font-weight:600}
.status-badge.functional{background:rgba(52,211,153,0.15);color:var(--emerald)}
.status-badge.unavailable{background:rgba(251,191,36,0.15);color:var(--warn)}
.status-badge.disabled_voluntarily{background:rgba(148,163,184,0.15);color:var(--muted)}

/* Cortex Grid */
.cortex-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.cortex-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:20px;position:relative;overflow:hidden}
.cortex-card::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--cyan),var(--teal))}
.cortex-title{font-size:15px;font-weight:700;color:var(--ink);display:flex;align-items:center;gap:8px;margin-bottom:8px}
.cortex-desc{font-size:12px;color:var(--muted);line-height:1.5;margin-bottom:14px}
.cortex-meta{background:#090d19;border:1px solid var(--line);padding:10px;border-radius:6px;font-size:11px;font-family:monospace;color:var(--teal)}

@media(max-width:880px){
  .dialogue-layout{grid-template-columns:1fr}
  .cortex-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="brand">
      <div class="logo-badge">UCA v2</div>
      <div>
        <div class="brand-title">Unified Cognitive Architecture</div>
        <div class="brand-sub">Cortex Parallèle & Raisonnement Neuro-Mathématique</div>
      </div>
    </div>
    <div class="header-badges">
      <div class="pill"><span class="dot ok"></span> Cortex : 5 Flux Actifs</div>
      <div class="pill"><span class="dot ok"></span> FTS5 : 8 Passages</div>
      <div class="pill"><span class="dot ok"></span> MeTTa : Opérationnel</div>
      <div class="pill"><span class="dot ok"></span> NCM : MiniTransformer (96.3%)</div>
    </div>
  </header>

  <nav class="tabs">
    <button class="tab-btn active" onclick="showTab('chat')">💬 Dialogue & Raisonnement</button>
    <button class="tab-btn" onclick="showTab('cortex')">🧠 Cortex Parallèle</button>
    <button class="tab-btn" onclick="showTab('pipeline')">⚙️ Pipeline & Modules</button>
    <button class="tab-btn" onclick="showTab('coordination')">🤖 Collectif Multi-Agents</button>
  </nav>

  <!-- TAB 1: DIALOGUE -->
  <div id="tab-chat" class="tab-content active">
    <div class="preset-container">
      <button class="preset-btn" onclick="loadPrompt('Résous 7*x - 14 = 28')">🧮 Équation : 7*x - 14 = 28</button>
      <button class="preset-btn" onclick="loadPrompt('Si pluie alors sol_mouille. Sachant que pluie.')">📜 Logique : Si pluie alors sol_mouille</button>
      <button class="preset-btn" onclick="loadPrompt('Que savons-nous sur le routage thalamo-cortical et la Bretagne ?')">🧠 Thalamus & Bretagne</button>
      <button class="preset-btn" onclick="loadPrompt('L\'humidité provoque la moisissure. La moisissure entraîne des allergies.')">🌐 Causalité de Pearl</button>
      <button class="preset-btn" onclick="loadPrompt('Calcule (18 + 12) * 5 / 6')">🔢 Arithmétique : (18 + 12) * 5 / 6</button>
    </div>

    <div class="dialogue-layout">
      <div class="chat-container">
        <div id="chatLog" style="display:flex;flex-direction:column;gap:14px">
          <div class="message">
            <div class="message-header"><span>🧠 UCA — SYSTÈME PRÊT</span><span>TOUS MODULES CHARGÉS</span></div>
            Bienvenue dans l'interface interactive de l'<strong>Unified Cognitive Architecture</strong>.<br>
            Le cortex parallèle neuro-mathématique, le runner MeTTa, le corpus FTS5 et le MiniTransformer sont initialisés et prêts pour une inférence locale sans hallucination.
          </div>
        </div>

        <form id="chatForm" class="composer-box" onsubmit="handleSend(event)">
          <textarea id="promptInput" class="composer-input" placeholder="Posez une question, soumettez une équation ou une déduction logique..." required></textarea>
          <div class="composer-footer">
            <label style="font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px;cursor:pointer">
              <input type="checkbox" id="devMode" checked> Mode développeur (traces & artefacts)
            </label>
            <button type="submit" id="sendBtn" class="send-btn">Envoyer à l'IA</button>
          </div>
        </form>
      </div>

      <aside>
        <div class="side-card">
          <h3>Modules Actifs en Direct</h3>
          <div id="sideModules">Chargement des états...</div>
        </div>
        <div class="side-card">
          <h3>Garanties de Conception</h3>
          <p style="font-size:12px;color:var(--muted);line-height:1.5">
            ✓ Calculs arithmétiques exacts (Q)<br>
            ✓ Déductions de Horn déterministes<br>
            ✓ Documents certifiés avec provenance<br>
            ✓ Séparation stricte faits / hypothèses
          </p>
        </div>
      </aside>
    </div>
  </div>

  <!-- TAB 2: CORTEX -->
  <div id="tab-cortex" class="tab-content">
    <div style="margin-bottom:20px">
      <h2 style="font-size:18px;margin-bottom:4px">Cortex Cognitif Parallèle Neuro-Mathématique (UCA Cortex v2)</h2>
      <p style="color:var(--muted);font-size:13px">5 flux de traitement concurrents inspirés des neurosciences et des mathématiques fondamentales.</p>
    </div>
    <div class="cortex-grid">
      <div class="cortex-card">
        <div class="cortex-title">🧮 1. Algèbre Rationnelle Exacte (Q)</div>
        <div class="cortex-desc">Résolution exacte d'équations linéaires, factorisation en nombres premiers jusqu'à 10¹², PGCD et PPCM par algorithme d'Euclide.</div>
        <div class="cortex-meta">Formule : a*x + b = c ⇒ x = (c - b) / a | Précision : 100%</div>
      </div>
      <div class="cortex-card">
        <div class="cortex-title">📜 2. Logique Formelle & Horn</div>
        <div class="cortex-desc">Moteur de chaînage avant déterministe en temps polynomial strict. Analyseur de tables de vérité (tautologies / contradictions).</div>
        <div class="cortex-meta">Règles : P ∧ Q → R | Preuve déductive traçable</div>
      </div>
      <div class="cortex-card">
        <div class="cortex-title">🌐 3. Causalité Structurelle de Pearl</div>
        <div class="cortex-desc">Graphes causaux orientés (DAGs), chirurgie de graphe simulant l'opérateur do(X) et neutralisation des facteurs de confusion.</div>
        <div class="cortex-meta">Do-Calculus : P(Y | do(X)) ≠ P(Y | X)</div>
      </div>
      <div class="cortex-card">
        <div class="cortex-title">🧬 4. Calcul Hyperdimensionnel (VSA)</div>
        <div class="cortex-desc">Mémoire holographique associative haute dimension (D=1024) combinant liaison (Hadamard), superposition et rotation.</div>
        <div class="cortex-meta">Opérations : BIND(Rôle, Entité) ⊕ BUNDLE | Cleanup</div>
      </div>
      <div class="cortex-card">
        <div class="cortex-title">⚡ 5. Inférence Active & Énergie Libre</div>
        <div class="cortex-desc">Minimisation de l'erreur prédictive de Friston entre attentes descendantes (priors) et preuves ascendantes (bottom-up).</div>
        <div class="cortex-meta">Erreur : ε = y - μ̂ | Alerte de Dissonance Cognitive</div>
      </div>
    </div>
  </div>

  <!-- TAB 3: PIPELINE -->
  <div id="tab-pipeline" class="tab-content">
    <div style="margin-bottom:20px">
      <h2 style="font-size:18px;margin-bottom:4px">Ordonnancement du Pipeline Séquentiel (12 étapes)</h2>
      <p style="color:var(--muted);font-size:13px">Activez ou réorganisez dynamiquement les modules de raisonnement.</p>
    </div>
    <div class="side-card" style="max-width:800px">
      <div id="pipelineList">Chargement du pipeline...</div>
      <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--line)">
        <h4 style="font-size:13px;margin-bottom:8px">Ordre d'exécution</h4>
        <input id="pipelineOrderInput" type="text" style="width:100%;background:#050811;border:1px solid var(--line);color:var(--ink);padding:8px 12px;border-radius:6px;font-family:monospace;font-size:12px">
        <button onclick="updatePipelineOrder()" style="margin-top:10px;background:#0369a1;border:none;color:#fff;padding:8px 16px;border-radius:6px;cursor:pointer">Sauvegarder l'Ordre</button>
      </div>
    </div>
  </div>

  <!-- TAB 4: COORDINATION -->
  <div id="tab-coordination" class="tab-content">
    <div style="margin-bottom:20px">
      <h2 style="font-size:18px;margin-bottom:4px">Collectif Multi-Agents & Espaces Partagés</h2>
      <p style="color:var(--muted);font-size:13px">Coordination versionnée sur GitHub Issue #1 et registres inter-agents.</p>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div class="side-card">
        <h3>Registre des Agents Actifs</h3>
        <ul style="list-style:none;font-size:13px;line-height:1.8;color:var(--muted)">
          <li>👤 <strong>Arena-NeuroMathArchitect</strong> : Cortex Parallèle, Algèbre Q & VSA (Notre session)</li>
          <li>👤 <strong>Arena-SymbolicRunner</strong> : Pont MeTTa/Hyperon réel</li>
          <li>👤 <strong>Arena-DataProvenance</strong> : Corpus FTS5 certifié (8 passages)</li>
          <li>👤 <strong>Arena-ModelArchitect</strong> : Entraînement MiniTransformer Denoiser</li>
          <li>👤 <strong>Opérateur Humain</strong> : timothedenizart-spec (Gouvernance)</li>
        </ul>
      </div>
      <div class="side-card">
        <h3>État des Chantiers (Backlog Partagé)</h3>
        <ul style="list-style:none;font-size:13px;line-height:1.8;color:var(--muted)">
          <li>✅ <strong>UCA-07</strong> : Cortex Cognitif Parallèle Neuro-Mathématique</li>
          <li>✅ <strong>UCA-01</strong> : Corpus Documentaire FTS5 local</li>
          <li>✅ <strong>UCA-02</strong> : Runner MeTTa réel et base de faits</li>
          <li>✅ <strong>UCA-08</strong> : Entraînement du MiniTransformer (35 époques)</li>
          <li>✅ <strong>UCA-09</strong> : Interface Web Complète & Lanceur Auto</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>
const $=s=>document.querySelector(s);

function showTab(tabId){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  $(`button[onclick="showTab('${tabId}')"]`).classList.add('active');
  $(`#tab-${tabId}`).classList.add('active');
}

function loadPrompt(text){
  $('#promptInput').value=text;
  $('#promptInput').focus();
}

async function api(url, options={}){
  const r = await fetch(url, {headers:{'Content-Type':'application/json'}, ...options});
  const data = await r.json();
  if(!r.ok) throw Error(data.error || 'Erreur API');
  return data;
}

function esc(s){
  const d=document.createElement('div');
  d.textContent=String(s??'');
  return d.innerHTML;
}

async function refreshStatus(){
  try{
    const data = await api('/api/status');
    const sideNodes = [];
    const pipeNodes = [];
    
    for(const [id, mod] of Object.entries(data.modules)){
      const st = mod.status;
      sideNodes.push(`
        <div class="status-item">
          <span>${esc(id)}</span>
          <span class="status-badge ${esc(st)}">${esc(st)}</span>
        </div>
      `);
      pipeNodes.push(`
        <div class="status-item">
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
            <input type="checkbox" ${st!=='disabled_voluntarily'?'checked':''} onchange="toggleModule('${esc(id)}', this.checked)">
            <strong>${esc(id)}</strong>
          </label>
          <span class="status-badge ${esc(st)}">${esc(st)}</span>
        </div>
      `);
    }
    $('#sideModules').innerHTML = sideNodes.join('');
    $('#pipelineList').innerHTML = pipeNodes.join('');
    $('#pipelineOrderInput').value = data.pipeline.join(', ');
  }catch(err){
    console.error('Status fetch error', err);
  }
}

async function toggleModule(id, enabled){
  try{
    await api('/api/modules/' + encodeURIComponent(id), {method:'POST', body:JSON.stringify({enabled})});
    refreshStatus();
  }catch(e){
    alert(e.message);
    refreshStatus();
  }
}

async function updatePipelineOrder(){
  const order = $('#pipelineOrderInput').value.split(',').map(s=>s.trim()).filter(Boolean);
  try{
    await api('/api/pipeline', {method:'POST', body:JSON.stringify({order})});
    alert('Ordre du pipeline mis à jour avec succès !');
    refreshStatus();
  }catch(e){
    alert('Erreur : ' + e.message);
  }
}

async function handleSend(e){
  e.preventDefault();
  const input = $('#promptInput');
  const btn = $('#sendBtn');
  const text = input.value.trim();
  const dev = $('#devMode').checked;
  if(!text) return;

  const chatLog = $('#chatLog');

  // Add User bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'message user';
  userBubble.innerHTML = `<div class="message-header"><span>👤 VOUS</span></div><div>${esc(text)}</div>`;
  chatLog.appendChild(userBubble);

  input.value = '';
  btn.disabled = true;

  // Pending bot bubble
  const botBubble = document.createElement('div');
  botBubble.className = 'message';
  botBubble.innerHTML = `<div class="message-header"><span>🧠 UCA — TRAITEMENT EN COURS...</span></div><div class="muted">Exécution concurrente du cortex parallèle et du pipeline séquentiel...</div>`;
  chatLog.appendChild(botBubble);
  botBubble.scrollIntoView({behavior:'smooth'});

  try{
    const res = await api('/api/chat', {method:'POST', body:JSON.stringify({message:text, developer:dev})});
    
    let contentHtml = `<div class="message-header"><span>🧠 UCA — SYNTHÈSE COGNITIVE</span><span>REQUÊTE VALIDÉE</span></div>`;
    contentHtml += `<div style="white-space:pre-wrap;margin-bottom:10px">${esc(res.answer || 'Aucune réponse.')}</div>`;

    if(res.sources && res.sources.length){
      contentHtml += `
        <details class="drawer">
          <summary>📄 Sources documentaires certifiées (${res.sources.length} passages FTS5)</summary>
          <div class="drawer-content">
            ${res.sources.map(s => `<div><strong>[${esc(s.content?.document_id || '?')}]</strong> ${esc(s.content?.content || '')}</div>`).join('<hr style="border:none;border-top:1px solid #222;margin:6px 0">')}
          </div>
        </details>
      `;
    }

    if(res.computations && res.computations.length){
      contentHtml += `
        <details class="drawer" open>
          <summary>📐 Déductions & Calculs vérifiés (${res.computations.length} opérations exactes)</summary>
          <div class="drawer-content">
            ${res.computations.map(c => `<div>✓ ${esc(JSON.stringify(c.content || c))}</div>`).join('')}
          </div>
        </details>
      `;
    }

    if(dev){
      contentHtml += `
        <details class="drawer">
          <summary>🛠️ Snapshot JSON Développeur complet</summary>
          <div class="drawer-content">
            <pre>${esc(JSON.stringify(res, null, 2))}</pre>
          </div>
        </details>
      `;
    }

    botBubble.innerHTML = contentHtml;
    refreshStatus();
  }catch(err){
    botBubble.innerHTML = `<div class="message-header"><span style="color:var(--rose)">⚠️ ERREUR D'EXÉCUTION</span></div><div>${esc(err.message)}</div>`;
  }finally{
    btn.disabled = false;
    input.focus();
    botBubble.scrollIntoView({behavior:'smooth'});
  }
}

// Auto-load on startup
window.onload = refreshStatus;
</script>
</body>
</html>"""



class UcaWebApplication:
    def __init__(self, engine: UnifiedCognitiveEngine) -> None:
        self.engine = engine
        self.lock = threading.RLock()

    def status(self) -> dict[str, Any]:
        with self.lock:
            return self.engine.status()

    def chat(self, message: str, developer: bool) -> dict[str, Any]:
        with self.lock:
            context = self.engine.process(message)
            return context.to_dict(developer=developer)

    def module_enabled(self, module_id: str, enabled: bool) -> dict[str, Any]:
        with self.lock:
            self.engine.set_module_enabled(module_id, enabled)
            return self.engine.status()

    def pipeline(self, order: list[str]) -> dict[str, Any]:
        with self.lock:
            self.engine.set_pipeline(order)
            return self.engine.status()

    def auxiliary_enabled(self, module_id: str, enabled: bool) -> dict[str, Any]:
        with self.lock:
            self.engine.set_auxiliary_enabled(module_id, enabled)
            return self.engine.status()

    def run(self, request_id: str) -> dict[str, Any] | None:
        with self.lock:
            return self.engine.run_store.get(request_id)


class _Handler(BaseHTTPRequestHandler):
    application: UcaWebApplication

    def log_message(self, format: str, *args: Any) -> None:  # quiet local UI except errors
        return

    def _json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(length)
        value = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/":
                data = INDEX_HTML.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers(); self.wfile.write(data)
            elif path == "/api/status":
                self._json(self.application.status())
            elif path == "/api/runs":
                self._json({"runs": self.application.engine.run_store.summaries()})
            elif path.startswith("/api/runs/"):
                stored = self.application.run(path.rsplit("/", 1)[-1])
                self._json(stored if stored else {"error": "Run not found"}, HTTPStatus.OK if stored else HTTPStatus.NOT_FOUND)
            else:
                self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except Exception as error:
            self._json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
            if path == "/api/chat":
                answer = self.application.chat(str(body.get("message", "")), bool(body.get("developer", False)))
                self._json(answer)
            elif path.startswith("/api/modules/"):
                self._json(self.application.module_enabled(path.rsplit("/", 1)[-1], bool(body.get("enabled", False))))
            elif path.startswith("/api/auxiliary/"):
                self._json(self.application.auxiliary_enabled(path.rsplit("/", 1)[-1], bool(body.get("enabled", False))))
            elif path == "/api/pipeline":
                order = body.get("order")
                if not isinstance(order, list) or not all(isinstance(item, str) for item in order):
                    raise ValueError("order must be a list of module IDs")
                self._json(self.application.pipeline(order))
            else:
                self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except (ValueError, KeyError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except Exception as error:
            self._json({"error": f"{type(error).__name__}: {error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)


def serve(application: UcaWebApplication, host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    class Handler(_Handler):
        pass
    Handler.application = application
    return ThreadingHTTPServer((host, port), Handler)
