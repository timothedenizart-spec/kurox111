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
<title>Unified Cognitive Architecture</title>
<style>
:root{--bg:#0b1020;--panel:#121a2c;--line:#293553;--ink:#ebf0ff;--muted:#a7b2cf;--accent:#77d9b8;--warn:#f5bf63;--bad:#ff8895}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px system-ui,sans-serif}.shell{display:grid;grid-template-columns:290px minmax(0,1fr);min-height:100vh}.side{background:#0d1424;border-right:1px solid var(--line);padding:18px;overflow:auto}.main{max-width:1000px;width:100%;padding:26px;margin:auto}h1{font-size:20px;margin:0 0 4px}.sub,.muted{color:var(--muted)}.badge{border:1px solid var(--line);padding:2px 7px;border-radius:999px;font-size:11px;display:inline-block}.functional,.completed{color:var(--accent)}.unavailable,.non_validated{color:var(--warn)}.failed_execution{color:var(--bad)}.disabled_voluntarily{color:var(--muted)}.module{border-bottom:1px solid var(--line);padding:10px 0}.module label{display:flex;align-items:center;gap:7px}.reason{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.35}.chat{display:flex;flex-direction:column;gap:15px}.message{background:var(--panel);border:1px solid var(--line);padding:14px;border-radius:10px;white-space:pre-wrap;line-height:1.5}.user{border-color:#3c5b77}.composer{display:flex;gap:9px;position:sticky;bottom:0;background:var(--bg);padding:14px 0}textarea{flex:1;resize:vertical;min-height:58px;background:var(--panel);border:1px solid var(--line);border-radius:8px;color:var(--ink);padding:10px}button{background:#183e48;border:1px solid #367685;color:var(--ink);border-radius:7px;padding:8px 12px;cursor:pointer}button:disabled{opacity:.55;cursor:wait}.details{margin-top:18px}.details summary{cursor:pointer;color:var(--accent)}pre{overflow:auto;background:#080d19;border:1px solid var(--line);padding:12px;border-radius:8px;font-size:12px}.advanced{display:none;margin-top:16px;border-top:1px solid var(--line);padding-top:15px}.advanced.show{display:block}input[type=text]{width:100%;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:7px}.notice{color:var(--warn);font-size:12px;line-height:1.4}@media(max-width:760px){.shell{display:block}.side{border-right:0;border-bottom:1px solid var(--line)}}
</style></head><body><div class="shell"><aside class="side"><h1>UCA</h1><p class="sub">Une conversation · plusieurs systèmes tracés</p><p><label><input id="developer" type="checkbox"> Mode développeur</label></p><div id="cognitive"></div><div id="topology"></div><div id="modules">Chargement des modules…</div><div id="auxiliary"></div><div id="advanced" class="advanced"><b>Ordre avancé</b><p class="notice">Les dépendances connues ne peuvent pas être inversées. Les modules désactivés restent visibles.</p><input id="order" type="text"><p><button id="saveOrder">Mettre à jour l'ordre</button></p></div></aside><main class="main"><div class="chat" id="chat"><div class="message"><b>Unified Cognitive Architecture</b><br>Les systèmes locaux indisponibles seront signalés plutôt que simulés. Envoyez une demande pour lancer le pipeline séquentiel.</div></div><form class="composer" id="form"><textarea id="message" placeholder="Écrivez à l'IA unifiée…" required></textarea><button id="send">Envoyer</button></form></main></div>
<script>
const $=s=>document.querySelector(s);let dev=false;
function esc(s){const x=document.createElement('div');x.textContent=String(s??'');return x.innerHTML}
function add(text,who='uca'){const d=document.createElement('div');d.className='message '+(who==='user'?'user':'');d.innerHTML=who==='user'?esc(text):text;$('#chat').append(d);d.scrollIntoView({behavior:'smooth',block:'end'});return d}
async function api(url, options={}){const r=await fetch(url,{headers:{'Content-Type':'application/json'},...options});const x=await r.json();if(!r.ok)throw Error(x.error||'Erreur API');return x}
async function status(){const data=await api('/api/status');const control=data.cognitive_control||{};$('#cognitive').innerHTML=control.status?`<div class="module"><b>Contrôle cognitif</b> <span class="badge ${esc(control.status)}">${esc(control.status)}</span><div class="reason">${esc(control.scope||'')}</div></div>`:'';const topology=data.execution_topology||{};$('#topology').innerHTML=topology.mode?`<div class="module"><b>Topologie d'exécution</b> <span class="badge functional">${esc(topology.mode)}</span><div class="reason">${esc(topology.guarantee||'')} Modules parallèles : ${esc((topology.parallel_stage||[]).join(', ')||'aucun')}.</div></div>`:'';const nodes=[];for(const [id,item] of Object.entries(data.modules)){const st=item.status;nodes.push(`<div class="module"><label><input type="checkbox" data-id="${esc(id)}" ${st!=='disabled_voluntarily'?'checked':''}><b>${esc(id)}</b></label><span class="badge ${esc(st)}">${esc(st)}</span><div class="reason">${esc(item.reason||'')}</div></div>`)}$('#modules').innerHTML=nodes.join('');const aux=[];for(const [id,item] of Object.entries(data.auxiliary||{})){const st=item.status;aux.push(`<div class="module"><label><input type="checkbox" data-aux="${esc(id)}" ${st!=='disabled_voluntarily'?'checked':''}><b>${esc(id)} (auxiliaire)</b></label><span class="badge ${esc(st)}">${esc(st)}</span><div class="reason">${esc(item.reason||'')}</div></div>`)}$('#auxiliary').innerHTML=aux.length?'<p class="sub">Techniques auxiliaires</p>'+aux.join(''):'';$('#order').value=data.pipeline.join(', ');document.querySelectorAll('[data-id]').forEach(box=>box.onchange=async()=>{try{await api('/api/modules/'+encodeURIComponent(box.dataset.id),{method:'POST',body:JSON.stringify({enabled:box.checked})});status()}catch(e){alert(e.message);box.checked=!box.checked}});document.querySelectorAll('[data-aux]').forEach(box=>box.onchange=async()=>{try{await api('/api/auxiliary/'+encodeURIComponent(box.dataset.aux),{method:'POST',body:JSON.stringify({enabled:box.checked})});status()}catch(e){alert(e.message);box.checked=!box.checked}})}
$('#developer').onchange=e=>{dev=e.target.checked;$('#advanced').classList.toggle('show',dev)};
$('#saveOrder').onclick=async()=>{try{const order=$('#order').value.split(',').map(x=>x.trim()).filter(Boolean);await api('/api/pipeline',{method:'POST',body:JSON.stringify({order})});status()}catch(e){alert(e.message)}};
$('#form').onsubmit=async e=>{e.preventDefault();const input=$('#message'),button=$('#send'),text=input.value.trim();if(!text)return;add(text,'user');input.value='';button.disabled=true;const pending=add('Exécution séquentielle des modules…');try{const result=await api('/api/chat',{method:'POST',body:JSON.stringify({message:text,developer:dev})});pending.innerHTML=esc(result.answer||'Aucune réponse finale.');if(dev){const trace=document.createElement('details');trace.className='details';trace.open=true;trace.innerHTML='<summary>Trace, sources et résultats intermédiaires</summary><pre>'+esc(JSON.stringify(result,null,2))+'</pre>';pending.append(trace)}status()}catch(err){pending.innerHTML='<b>Erreur :</b> '+esc(err.message)}finally{button.disabled=false;input.focus()}};
status().catch(e=>$('#modules').textContent='État indisponible : '+e.message);
</script></body></html>"""


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
