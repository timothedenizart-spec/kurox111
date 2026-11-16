/*
 * ÉCLIPSE — vertical slice local
 * Toutes les durées sont des conventions de jeu. Elles servent à produire
 * des signaux narratifs et ne constituent pas des recommandations de santé.
 */
(() => {
  "use strict";

  const HOUR = 60 * 60 * 1000;
  const DAY = 24 * HOUR;
  const STORAGE_KEY = "eclipse-chronique-v1";
  const STARTING_NOTE = "La radio évoque un foyer respiratoire. Dans l’immeuble, personne ne sait encore quoi en penser.";

  const PHASES = [
    {
      key: "signal",
      fromDay: 0,
      kicker: "SIGNALEMENT LOCAL",
      title: "Les volets sont encore ouverts.",
      description: "La ville travaille, paie et attend. À la radio, on parle d’un foyer respiratoire sans gravité confirmée.",
      pulse: "Les bus circulent encore.",
      cityStatus: "activité ordinaire",
      health: "quelques signalements isolés",
      civic: "la mairie recommande la prudence",
      economy: "les prix restent stables",
      bulletin: "Les habitants sont invités à conserver leurs habitudes, tout en évitant les rassemblements non essentiels.",
      street: "Une voisine sort les poubelles sans vous regarder. Dans l’immeuble, quelqu’un tousse derrière une porte."
    },
    {
      key: "doubt",
      fromDay: 2,
      kicker: "JOUR {day} · CONSIGNES CHANGEANTES",
      title: "On commence à compter les absences.",
      description: "Les informations se contredisent. Les collègues manquent à l’appel, mais les vitrines sont encore éclairées le soir.",
      pulse: "La ligne de bus passe moins souvent.",
      cityStatus: "vigilance discrète",
      health: "les cabinets demandent de rappeler plus tard",
      civic: "des consignes circulent sans être claires",
      economy: "les livraisons prennent du retard",
      bulletin: "La préfecture demande aux employeurs d’aménager les horaires. Aucune restriction officielle n’est annoncée à cette heure.",
      street: "Devant l’épicerie, les gens gardent davantage leurs distances. Personne n’avoue avoir peur."
    },
    {
      key: "pressure",
      fromDay: 6,
      kicker: "JOUR {day} · PRESSION SANITAIRE",
      title: "Les files remplacent les habitudes.",
      description: "La maladie est désormais visible dans les silences. Les livraisons s’espacent, les pharmacies limitent leurs entrées.",
      pulse: "Les rideaux métalliques restent baissés plus longtemps.",
      cityStatus: "accès restreint",
      health: "les urgences filtrent les arrivées",
      civic: "les messages publics deviennent plus brefs",
      economy: "certains produits partent avant midi",
      bulletin: "Les commerces essentiels ajustent leurs horaires. Il est demandé de ne pas stocker au-delà du nécessaire.",
      street: "Un sac de courses reste quelques minutes devant une porte. Personne n’ose sonner tout de suite."
    },
    {
      key: "breakdown",
      fromDay: 11,
      kicker: "JOUR {day} · RUPTURE DES SERVICES",
      title: "La ville ne répond plus comme avant.",
      description: "L’argent circule encore, mais les mots “ouvert” et “disponible” ont perdu leur sens. Chacun se replie sur ses proches.",
      pulse: "Au loin, une sirène s’interrompt trop tôt.",
      cityStatus: "rupture imminente",
      health: "des rues entières restent sans nouvelles",
      civic: "les appels publics sont intermittents",
      economy: "l’argent ne garantit plus un stock",
      bulletin: "Message automatique : les habitants doivent limiter tout déplacement. Les équipes locales sont mobilisées sur des priorités urgentes.",
      street: "La place est presque vide. Un vélo renversé reste là depuis hier, sous une pluie fine."
    },
    {
      key: "alteration",
      fromDay: 18,
      kicker: "JOUR {day} · COMPORTEMENTS INEXPLIQUÉS",
      title: "Quelque chose a changé dans les rues.",
      description: "Les derniers messages évoquent des réactions imprévisibles. La monnaie ne rassure plus personne : l’eau, l’abri et les liens comptent davantage.",
      pulse: "Le quartier écoute avant d’ouvrir.",
      cityStatus: "survie locale",
      health: "les observations ne correspondent plus aux bulletins",
      civic: "aucune consigne fiable ne circule",
      economy: "les échanges directs remplacent les achats",
      bulletin: "Transmission brouillée. Voix non identifiée : « Ne sortez pas seul. Écoutez les portes avant de les ouvrir. »",
      street: "Une silhouette traverse la place en saccades. Plus personne ne reste près des vitrines."
    }
  ];

  const NEEDS = [
    {
      id: "drink", label: "Hydratation", symbol: "≈", comfort: 2 * HOUR, alert: 4 * HOUR, critical: 7 * HOUR,
      calm: "Vous n’y pensez pas.", notice: "Votre bouche se dessèche un peu.", urgent: "La soif rend chaque décision plus courte.", action: "Boire un peu", detail: "utilise une eau"
    },
    {
      id: "food", label: "Énergie", symbol: "·", comfort: 5 * HOUR, alert: 8 * HOUR, critical: 14 * HOUR,
      calm: "Votre ventre reste silencieux.", notice: "Vous cherchez quelque chose de consistant.", urgent: "Votre attention revient sans cesse à la nourriture.", action: "Manger", detail: "utilise une ration"
    },
    {
      id: "rest", label: "Repos", symbol: "∿", comfort: 14 * HOUR, alert: 17 * HOUR, critical: 21 * HOUR,
      calm: "Vous avez encore les idées claires.", notice: "Vos gestes perdent un peu de précision.", urgent: "Vos paupières tirent ; le monde paraît plus lent.", action: "Vous allonger", detail: "enregistre le début d’un repos"
    },
    {
      id: "wash", label: "Hygiène", symbol: "◌", comfort: 20 * HOUR, alert: 32 * HOUR, critical: 48 * HOUR,
      calm: "Vous vous sentez présentable.", notice: "Une douche vous ferait du bien.", urgent: "Vous ne vous sentez plus vraiment à l’aise dans vos vêtements.", action: "Vous rafraîchir", detail: "utilise un peu d’eau"
    },
    {
      id: "relief", label: "Intimité", symbol: "□", comfort: 3 * HOUR, alert: 5 * HOUR, critical: 7 * HOUR,
      calm: "Rien ne vous presse.", notice: "Vous repérez les toilettes dès que vous entrez quelque part.", urgent: "Il devient difficile de penser à autre chose.", action: "Prendre un moment", detail: "chez vous, porte fermée"
    },
    {
      id: "contact", label: "Lien humain", symbol: "+", comfort: 22 * HOUR, alert: 42 * HOUR, critical: 72 * HOUR,
      calm: "Les présences autour de vous suffisent.", notice: "Une voix familière vous ferait du bien.", urgent: "Le silence de l’immeuble devient lourd.", action: "Prendre des nouvelles", detail: "un appel bref"
    }
  ];

  const PEOPLE_TEMPLATE = [
    ["Lucie Morel", "infirmière de nuit", "4A"], ["Noé Martin", "livreur", "1B"], ["Samira Benyahia", "gérante de l’épicerie", "rue"],
    ["Émile Caron", "retraité", "2A"], ["Iris Vidal", "étudiante", "5C"], ["Hugo Perrin", "chauffeur de bus", "3A"],
    ["Lina Abadie", "pharmacienne", "angle nord"], ["Jo Costa", "cuisinier", "5A"], ["Mireille Thomas", "concierge", "rez-de-chaussée"],
    ["Yanis Diallo", "technicien réseau", "2C"], ["Claire Roux", "professeure", "4B"], ["Ruben Garcia", "agent municipal", "place"],
    ["Nina Dumas", "musicienne", "1A"], ["Basile Fournier", "agent d’entretien", "3C"], ["Awa Traoré", "bibliothécaire", "2B"],
    ["Marc Sorel", "vigile", "5B"], ["Sofia Ricci", "couturière", "3B"], ["Théo Giraud", "apprenti", "1C"]
  ];

  const $ = (selector) => document.querySelector(selector);
  const els = {
    watchDate: $("#watch-date"), watchTime: $("#watch-time"), phaseKicker: $("#phase-kicker"), phaseTitle: $("#phase-title"),
    phaseDescription: $("#phase-description"), cityPulse: $("#city-pulse"), cityStatus: $("#city-status"), bulletin: $("#bulletin"),
    bulletinTime: $("#bulletin-time"), money: $("#money-value"), inventory: $("#inventory"), needs: $("#needs-list"),
    selfActions: $("#self-actions"), intent: $("#intent-text"), cityMap: $("#city-map"), residents: $("#resident-list"),
    residentSummary: $("#resident-summary"), worldSignals: $("#world-signals"), supplies: $("#supply-list"), streetStory: $("#street-story"),
    noteCount: $("#note-count"), modalBackdrop: $("#modal-backdrop"), modalKicker: $("#modal-kicker"), modalTitle: $("#modal-title"),
    modalContent: $("#modal-content"), toast: $("#toast")
  };

  let state = loadState();
  let toastTimer;

  function createInitialState() {
    const now = Date.now();
    const people = PEOPLE_TEMPLATE.map((entry, index) => ({
      id: `p-${index}`, name: entry[0], role: entry[1], home: entry[2],
      mobility: 0.25 + ((index * 17) % 60) / 100,
      resources: 1 + (index % 3), trust: 0.35 + ((index * 29) % 50) / 100,
      health: index === 1 ? "incubation" : "well", infectedAt: index === 1 ? now - 13 * HOUR : null,
      lastObservation: now - (index % 7) * HOUR, memories: []
    }));
    return {
      version: 1,
      startedAt: now,
      lastUpdatedAt: now,
      simulatedAt: now,
      phaseSeen: 0,
      seed: (now % 2147483646) + 1,
      money: 86,
      inventory: { water: 2, ration: 2, soap: 1, radio: 1, watch: 1 },
      needs: { drink: now - 30 * 60 * 1000, food: now - 2 * HOUR, rest: now - 8 * HOUR, wash: now - 11 * HOUR, relief: now - 1 * HOUR, contact: now - 9 * HOUR },
      restingSince: null,
      people,
      notes: [{ at: now, text: STARTING_NOTE }],
      observed: [],
      purchases: {},
      lastStreetObservation: 0
    };
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (saved && saved.version === 1 && saved.startedAt && saved.people && saved.needs) return saved;
    } catch (error) {
      console.warn("Sauvegarde Éclipse illisible", error);
    }
    return createInitialState();
  }

  function saveState() {
    state.lastUpdatedAt = Date.now();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function rand() {
    state.seed = (state.seed * 48271) % 2147483647;
    return state.seed / 2147483647;
  }

  function elapsedDays(now = Date.now()) { return Math.max(0, (now - state.startedAt) / DAY); }
  function gameDay(now = Date.now()) { return Math.floor(elapsedDays(now)) + 1; }
  function phaseIndex(now = Date.now()) {
    const day = elapsedDays(now);
    let index = 0;
    PHASES.forEach((phase, i) => { if (day >= phase.fromDay) index = i; });
    return index;
  }
  function currentPhase(now = Date.now()) { return PHASES[phaseIndex(now)]; }
  function formatted(value) { return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value); }
  function formatDate(date) { return new Intl.DateTimeFormat("fr-FR", { weekday: "short", day: "2-digit", month: "short" }).format(date).replace(".", ""); }
  function formatTime(date) { return new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit", hour12: false }).format(date); }
  function noteTime(timestamp) { return `${formatDate(new Date(timestamp))} · ${formatTime(new Date(timestamp))}`; }
  function replaceDay(text, now = Date.now()) { return text.replace("{day}", gameDay(now)); }

  function isInfectious(person) { return ["incubation", "symptomatic", "severe", "altered"].includes(person.health); }
  function simulateUntil(now) {
    let cursor = state.simulatedAt || now;
    const maximumSteps = 24 * 60; // limitation défensive : soixante jours au retour d’une très vieille sauvegarde
    let steps = 0;
    while (cursor + HOUR <= now && steps < maximumSteps) {
      cursor += HOUR;
      simulateHour(cursor);
      steps += 1;
    }
    state.simulatedAt = cursor;
  }

  function simulateHour(at) {
    const phase = phaseIndex(at);
    const infectious = state.people.filter(isInfectious).length;
    const activeRatio = infectious / state.people.length;
    state.people.forEach((person) => {
      const sinceInfection = person.infectedAt ? at - person.infectedAt : 0;
      if (person.health === "well") {
        const phasePressure = [0.0005, 0.0013, 0.0025, 0.004, 0.0055][phase];
        const chance = phasePressure * (0.35 + person.mobility) * (0.4 + activeRatio * 7);
        if (rand() < chance) {
          person.health = "exposed";
          person.infectedAt = at;
          person.memories.push("a croisé quelqu’un qui semblait très affaibli");
        }
      } else if (person.health === "exposed" && sinceInfection > (8 + Math.floor(rand() * 12)) * HOUR) {
        person.health = "incubation";
      } else if (person.health === "incubation" && sinceInfection > (30 + Math.floor(rand() * 27)) * HOUR) {
        person.health = "symptomatic";
      } else if (person.health === "symptomatic" && sinceInfection > (84 + Math.floor(rand() * 30)) * HOUR && rand() < .15) {
        person.health = "severe";
      } else if (person.health === "severe" && phase >= 4 && sinceInfection > 6 * DAY && rand() < .19) {
        person.health = "altered";
      }
      if (rand() < .08 + phase * .025) person.lastObservation = at;
    });
  }

  function getNeed(need, now = Date.now()) {
    const last = state.needs[need.id] || now;
    const since = now - last;
    if (need.id === "rest" && state.restingSince) {
      const restingFor = now - state.restingSince;
      if (restingFor >= 4 * HOUR) {
        state.needs.rest = now;
        state.restingSince = null;
        addNote("Vous avez dormi assez longtemps pour remettre vos pensées en ordre.", now, false);
        return { level: "calm", message: need.calm };
      }
      return { level: "notice", message: "Vous vous reposez. Laissez passer du temps réel." };
    }
    if (since < need.comfort) return { level: "calm", message: need.calm };
    if (since < need.alert) return { level: "notice", message: need.notice };
    return { level: "urgent", message: need.urgent };
  }

  function addNote(text, at = Date.now(), shouldToast = true) {
    const duplicate = state.notes.some((note) => note.text === text && Math.abs(note.at - at) < HOUR);
    if (!duplicate) {
      state.notes.unshift({ at, text });
      state.notes = state.notes.slice(0, 30);
    }
    if (shouldToast) showToast("Ajouté au carnet.");
  }

  function cityPlaces(phase) {
    const grocery = [
      ["Ouvert jusqu’à 20 h", "open"], ["Ouvert, files courtes", "open"], ["Quota discret le matin", "limited"], ["Rideau à demi baissé", "limited"], ["Fermé — livraisons coupées", "closed"]
    ][phase];
    const pharmacy = [
      ["Sans attente", "open"], ["Entrées espacées", "limited"], ["File à l’extérieur", "limited"], ["Comptoir prioritaire", "limited"], ["Volet fermé", "closed"]
    ][phase];
    const cafe = [
      ["Tables pleines", "open"], ["Service réduit", "limited"], ["Fermé par précaution", "closed"], ["Fermé", "closed"], ["Fermé", "closed"]
    ][phase];
    return [
      { id: "home", name: "Chez vous", code: "3B · REFUGE", status: "Porte fermée, eau courante", type: "home", state: "open" },
      { id: "grocery", name: "Épicerie Morel", code: "RUE · 40 M", status: grocery[0], type: "shop", state: grocery[1] },
      { id: "pharmacy", name: "Pharmacie Vidal", code: "ANGLE · 80 M", status: pharmacy[0], type: "pharmacy", state: pharmacy[1] },
      { id: "square", name: "Place des Tilleuls", code: "CŒUR · 120 M", status: cafe[0], type: "square", state: cafe[1] }
    ];
  }

  function observationFor(person, phase) {
    const generic = ["des pas derrière la porte", "n’a pas été vu aujourd’hui", "laisse sa fenêtre entrouverte", "rentre avec un sac léger", "parle bas dans le couloir"];
    const byHealth = {
      well: generic,
      exposed: ["a l’air très pressé·e", "évite les regards", "reste plus souvent chez soi"],
      incubation: ["sort sans saluer", "a le visage fermé", "reste au téléphone longtemps"],
      symptomatic: ["tousse au palier", "laisse une porte close", "marche plus lentement"],
      severe: ["aucun mouvement derrière les rideaux", "ne répond plus à son nom", "les lumières restent allumées"],
      altered: ["mouvements désordonnés", "réagit au moindre bruit", "reste immobile près de l’entrée"]
    };
    const list = byHealth[person.health] || generic;
    const base = list[(person.id.length + Math.floor((Date.now() - person.lastObservation) / HOUR)) % list.length];
    return phase < 4 && person.health === "altered" ? "rideaux fermés depuis longtemps" : base;
  }

  function worldData(phase) {
    const people = state.people;
    const away = people.filter((person) => ["symptomatic", "severe", "altered"].includes(person.health)).length;
    const contact = phase === 0 ? "encore ordinaire" : phase < 3 ? "méfiant" : "très rare";
    return [
      { label: "Santé", value: currentPhase().health, tone: phase >= 3 ? "danger" : phase >= 2 ? "alert" : "" },
      { label: "Quartier", value: away ? `${away} voisin${away > 1 ? "s" : ""} semble${away > 1 ? "nt" : ""} absent${away > 1 ? "s" : ""}` : "les habitudes tiennent encore", tone: away > 3 ? "alert" : "" },
      { label: "Échanges", value: phase < 4 ? currentPhase().economy : "l’eau et l’abri valent plus que les billets", tone: phase >= 3 ? "alert" : "" },
      { label: "Confiance", value: `le voisinage devient ${contact}`, tone: "" }
    ];
  }

  function updatePhaseNote(now) {
    const index = phaseIndex(now);
    if ((state.phaseSeen ?? 0) !== index) {
      state.phaseSeen = index;
      addNote(`La ville entre dans une nouvelle phase : ${PHASES[index].kicker.replace("{day}", gameDay(now)).toLowerCase()}.`, now, true);
    }
  }

  function render(now = Date.now()) {
    simulateUntil(now);
    updatePhaseNote(now);
    const phaseNumber = phaseIndex(now);
    const phase = PHASES[phaseNumber];
    const day = gameDay(now);
    els.watchDate.textContent = formatDate(new Date(now));
    els.watchTime.textContent = formatTime(new Date(now));
    els.phaseKicker.textContent = replaceDay(phase.kicker, now).startsWith("JOUR") ? replaceDay(phase.kicker, now) : `JOUR ${day} · ${phase.kicker}`;
    els.phaseTitle.textContent = phase.title;
    els.phaseDescription.textContent = phase.description;
    els.cityPulse.textContent = phase.pulse;
    els.cityStatus.textContent = phase.cityStatus;
    els.bulletin.textContent = `« ${phase.bulletin} »`;
    els.bulletinTime.textContent = phaseNumber === 0 ? "maintenant" : "message conservé";
    els.money.textContent = formatted(state.money);
    els.noteCount.textContent = state.notes.length;
    renderInventory();
    renderNeeds(now);
    renderActions(now);
    renderMap(phaseNumber);
    renderPeople(phaseNumber);
    renderWorld(phaseNumber);
    renderSupplies();
    els.streetStory.textContent = phase.street;
    const resting = state.restingSince ? "Vous êtes allongée. La ville reste dehors." : (phaseNumber >= 3 ? "Vous êtes chez vous. Chaque sortie mérite d’être pesée." : "Vous êtes chez vous. La matinée est calme.");
    els.intent.textContent = resting;
    saveState();
  }

  function renderInventory() {
    const labels = [];
    if (state.inventory.watch) labels.push("⌚ montre");
    if (state.inventory.radio) labels.push("⌁ radio");
    if (state.inventory.soap) labels.push("◌ savon");
    els.inventory.innerHTML = labels.map((item) => `<span>${item}</span>`).join("");
  }

  function renderNeeds(now) {
    els.needs.innerHTML = NEEDS.map((need) => {
      const result = getNeed(need, now);
      return `<div class="need-row ${result.level}"><span class="need-symbol">${need.symbol}</span><div class="need-copy"><span class="need-name">${need.label}</span><span class="need-message">${result.message}</span></div></div>`;
    }).join("");
  }

  function renderActions(now) {
    const restLabel = state.restingSince ? "Vous lever" : "Vous allonger";
    const actions = [
      { id: "drink", label: "Boire un peu", detail: state.inventory.water ? "utilise une eau" : "aucune eau disponible", disabled: !state.inventory.water },
      { id: "food", label: "Manger", detail: state.inventory.ration ? "utilise une ration" : "aucune ration disponible", disabled: !state.inventory.ration },
      { id: "rest", label: restLabel, detail: state.restingSince ? "mettre fin au repos" : "le temps reste réel", disabled: false },
      { id: "wash", label: "Vous rafraîchir", detail: state.inventory.water ? "utilise un peu d’eau" : "eau nécessaire", disabled: !state.inventory.water },
      { id: "relief", label: "Prendre un moment", detail: "porte fermée", disabled: false },
      { id: "contact", label: "Prendre des nouvelles", detail: "un appel bref", disabled: false }
    ];
    els.selfActions.innerHTML = actions.map((action) => `<button class="action-button" data-action="${action.id}" type="button" ${action.disabled ? "disabled" : ""}><span>${action.label}<small>${action.detail}</small></span><b>›</b></button>`).join("");
  }

  function renderMap(phase) {
    const places = cityPlaces(phase);
    els.cityMap.innerHTML = places.map((place) => `<button type="button" class="place place-${place.type} ${place.state === "closed" ? "closed" : ""}" data-place="${place.id}"><span class="place-code">${place.code}</span><strong>${place.name}</strong><small class="${place.state === "closed" ? "status-closed" : ""}">${place.status}</small></button>`).join("");
  }

  function renderPeople(phase) {
    const sorted = [...state.people].sort((a, b) => {
      const score = { altered: 0, severe: 1, symptomatic: 2, incubation: 3, exposed: 4, well: 5 };
      return score[a.health] - score[b.health];
    });
    const shown = sorted.slice(0, 6);
    els.residentSummary.textContent = `${state.people.length} profils locaux`;
    els.residents.innerHTML = shown.map((person) => {
      const first = person.name[0];
      return `<button type="button" class="resident" data-resident="${person.id}"><span class="resident-avatar">${first}</span><span class="resident-main"><strong>${person.name}</strong><span>${person.role} · ${person.home}</span></span><span class="resident-observation">${observationFor(person, phase)}</span></button>`;
    }).join("");
  }

  function renderWorld(phase) {
    els.worldSignals.innerHTML = worldData(phase).map((item) => `<div class="world-signal"><span class="label">${item.label}</span><strong class="${item.tone}">${item.value}</strong></div>`).join("");
  }

  function renderSupplies() {
    const resources = [
      ["Eau potable", state.inventory.water, "unité"], ["Rations", state.inventory.ration, "unité"], ["Savon", state.inventory.soap, "pain"], ["Batterie radio", state.inventory.radio, "chargée"]
    ];
    els.supplies.innerHTML = resources.map(([name, qty, unit]) => `<div class="supply-line ${qty ? "" : "empty"}"><span>${name}</span><span>${qty ? `${qty} ${unit}${qty > 1 && unit === "unité" ? "s" : ""}` : "épuisé"}</span></div>`).join("");
  }

  function doAction(action) {
    const now = Date.now();
    if (action === "drink" && state.inventory.water) {
      state.inventory.water -= 1; state.needs.drink = now; addNote("Vous avez bu lentement, debout près de l’évier.", now); showToast("Un peu de répit.");
    } else if (action === "food" && state.inventory.ration) {
      state.inventory.ration -= 1; state.needs.food = now; addNote("Vous avez mangé une ration sans quitter la cuisine.", now); showToast("Vous reprenez des forces.");
    } else if (action === "wash" && state.inventory.water) {
      state.inventory.water -= 1; state.needs.wash = now; addNote("Vous vous êtes rafraîchie avec l’eau disponible.", now); showToast("Un geste simple, mais utile.");
    } else if (action === "relief") {
      state.needs.relief = now; showToast("Vous prenez un instant pour vous.");
    } else if (action === "contact") {
      state.needs.contact = now;
      const person = state.people.find((entry) => entry.health === "well") || state.people[0];
      addNote(`Vous avez laissé un message à ${person.name}. La réponse viendra peut-être plus tard.`, now);
      showToast("La sonnerie semble trop longue.");
    } else if (action === "rest") {
      if (state.restingSince) {
        const duration = now - state.restingSince;
        state.restingSince = null;
        if (duration >= 45 * 60 * 1000) {
          // Une courte pause atténue la dette de repos sans simuler une nuit entière.
          state.needs.rest = Math.min(now, state.needs.rest + Math.floor(duration * 0.6));
          addNote("Vous vous levez après une courte pause. Ce n’était pas une nuit, mais cela aide.", now);
          showToast("Vous reprenez vos esprits.");
        } else {
          showToast("Vous n’avez fait que vous allonger quelques instants.");
        }
      } else {
        state.restingSince = now;
        addNote("Vous vous êtes allongée. Le repos se mesure au temps réellement laissé au calme.", now);
        showToast("La ville continue sans vous.");
      }
    }
    render(now);
  }

  function shopPrice(item, phase) { return Math.round(item.base * (1 + phase * .31) * 100) / 100; }
  function purchase(shop, itemId) {
    const phase = phaseIndex();
    const inventory = {
      grocery: [
        { id: "water", label: "Eau scellée", desc: "une bouteille pour le sac", base: 1.8, available: phase < 4 },
        { id: "ration", label: "Ration simple", desc: "conserve et pain sec", base: 4.5, available: phase < 4 }
      ],
      pharmacy: [
        { id: "soap", label: "Savon solide", desc: "hygiène de base", base: 3.2, available: phase < 4 },
        { id: "water", label: "Eau scellée", desc: "stock très limité", base: 2.4, available: phase < 3 }
      ]
    };
    const item = inventory[shop]?.find((entry) => entry.id === itemId);
    if (!item || !item.available) { showToast("Ce produit n’est plus disponible ici."); return; }
    const price = shopPrice(item, phase);
    if (state.money < price) { showToast("Vous n’avez pas assez d’espèces."); return; }
    const key = `${gameDay()}-${shop}-${item.id}`;
    if (state.purchases[key]) { showToast("La vente est limitée à une unité aujourd’hui."); return; }
    state.money = Math.round((state.money - price) * 100) / 100;
    state.inventory[item.id] = (state.inventory[item.id] || 0) + 1;
    state.purchases[key] = true;
    addNote(`Vous avez acheté ${item.label.toLowerCase()} à ${shop === "grocery" ? "l’épicerie" : "la pharmacie"} pour ${formatted(price)}.`, Date.now());
    closeModal();
    render();
  }

  function openPlace(placeId) {
    const phase = phaseIndex();
    const place = cityPlaces(phase).find((entry) => entry.id === placeId);
    if (!place) return;
    if (placeId === "home") {
      openModal("REFUGE", "Appartement 3B", `<p class="modal-info">Votre porte est fermée. L’eau coule encore, l’électricité tient par intermittence et votre montre donne une forme aux heures.</p><p class="modal-info">Un refuge n’est jamais totalement sûr : c’est un endroit où l’on peut enfin écouter ce qui se passe dehors.</p>`);
      return;
    }
    if (placeId === "square") {
      const copy = phase < 2 ? "Des gens coupent par la place sans trop ralentir. Le café laisse encore sortir une odeur de grains brûlés." : phase < 4 ? "Les bancs sont vides. Les conversations se coupent quand quelqu’un approche." : "Le vent pousse une publicité froissée contre le trottoir. Vous ne vous attardez pas.";
      openModal("LIEU OBSERVÉ", "Place des Tilleuls", `<p class="modal-info">${copy}</p><button class="modal-action" data-modal-action="observe-square">Rester quelques minutes et observer</button>`);
      return;
    }
    if (place.state === "closed") {
      openModal("COMMERCE FERMÉ", place.name, `<p class="modal-info">${place.status}. Derrière la vitre, les rayons semblent plus vides que la dernière fois.</p>`);
      return;
    }
    const stock = placeId === "grocery" ? [
      { id: "water", label: "Eau scellée", desc: "une bouteille pour le sac", base: 1.8, available: phase < 4 },
      { id: "ration", label: "Ration simple", desc: "conserve et pain sec", base: 4.5, available: phase < 4 }
    ] : [
      { id: "soap", label: "Savon solide", desc: "hygiène de base", base: 3.2, available: phase < 4 },
      { id: "water", label: "Eau scellée", desc: "stock très limité", base: 2.4, available: phase < 3 }
    ];
    const rows = stock.map((item) => {
      const key = `${gameDay()}-${placeId}-${item.id}`;
      const disabled = !item.available || state.purchases[key] || state.money < shopPrice(item, phase);
      const reason = !item.available ? "épuisé" : state.purchases[key] ? "quota atteint" : formatted(shopPrice(item, phase));
      return `<div class="buy-row"><div><strong>${item.label}</strong><span>${item.desc}</span></div><button data-buy="${placeId}:${item.id}" ${disabled ? "disabled" : ""}>${reason}</button></div>`;
    }).join("");
    openModal("COMMERCE", placeId === "grocery" ? "Épicerie Morel" : "Pharmacie Vidal", `<p class="modal-info">${place.status}. Les prix suivent l’incertitude, les stocks partent vite.</p><div class="buy-list">${rows}</div>`);
  }

  function openResident(id) {
    const person = state.people.find((entry) => entry.id === id);
    if (!person) return;
    const phase = phaseIndex();
    const observations = [
      `${person.name} est ${person.role}.`,
      `Domicile ou repère : ${person.home}.`,
      `Dernière impression : ${observationFor(person, phase)}.`,
      person.memories.length ? `Vous avez entendu qu’iel ${person.memories[person.memories.length - 1]}.` : "Vous ne savez pas ce qui se passe vraiment de l’autre côté de sa porte."
    ];
    const alreadyObserved = state.observed.includes(id);
    if (!alreadyObserved) {
      state.observed.push(id);
      addNote(`Observation : ${person.name} — ${observationFor(person, phase)}.`, Date.now(), false);
    }
    openModal("VOISINAGE", person.name, `<ul class="modal-list">${observations.map((entry) => `<li>${entry}</li>`).join("")}</ul><p class="modal-info"><strong>Vous ne voyez qu’un fragment.</strong> Les symptômes, les rumeurs et les silences ne sont pas des certitudes.</p>`);
    render();
  }

  function openModal(kicker, title, content) {
    els.modalKicker.textContent = kicker;
    els.modalTitle.textContent = title;
    els.modalContent.innerHTML = content;
    els.modalBackdrop.hidden = false;
    $("#close-modal").focus();
  }
  function closeModal() { els.modalBackdrop.hidden = true; }

  function openNotes() {
    const entries = state.notes.length ? state.notes.map((note) => `<article class="note-entry"><time>${noteTime(note.at)}</time><p>${note.text}</p></article>`).join("") : `<p class="empty-notes">Votre carnet est encore vide.</p>`;
    openModal("CARNET", "Vos observations", entries);
  }
  function openBodyInfo() {
    openModal("SYSTÈME DE SURVIE", "Votre corps ne se résume pas à une barre", `<p class="modal-info">Les besoins sont suivis avec des instants réels et se manifestent par des <strong>indices</strong>. Votre montre donne l’heure ; elle ne révèle ni pourcentage, ni compte à rebours.</p><p class="modal-info">Boire, manger, dormir, se laver, préserver son intimité et garder un lien sont des actions ordinaires qui deviennent plus difficiles lorsque la ville se défait.</p>`);
  }
  function openStash() {
    const all = [["Eau potable", state.inventory.water], ["Rations", state.inventory.ration], ["Savon", state.inventory.soap], ["Radio", state.inventory.radio ? "une, chargée" : "aucune"], ["Montre", state.inventory.watch ? "portée" : "aucune"]];
    openModal("SAC ET APPARTEMENT", "Ce que vous pouvez compter", `<ul class="modal-list">${all.map(([name, value]) => `<li><span>${name}</span><small>${value}</small></li>`).join("")}</ul><p class="modal-info">Ce qui importe change avec la crise. Les nombres restent pour vous, jamais sous forme de jauge de besoin.</p>`);
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    els.toast.textContent = message;
    els.toast.classList.add("visible");
    toastTimer = setTimeout(() => els.toast.classList.remove("visible"), 2800);
  }

  function restart() {
    openModal("RECOMMENCER", "Effacer cette chronique ?", `<p class="modal-info">Votre carnet, vos réserves et le voisinage repartiront au premier matin. Cette action ne peut pas être annulée.</p><button class="modal-action danger-action" data-modal-action="restart">Recommencer la partie</button>`);
  }

  function observeStreet() {
    const now = Date.now();
    if (now - state.lastStreetObservation < 10 * 60 * 1000) { showToast("Vous avez déjà pris le temps de regarder récemment."); return; }
    state.lastStreetObservation = now;
    const person = state.people[Math.floor(rand() * state.people.length)];
    const detail = `Depuis la fenêtre, vous apercevez ${person.name.split(" ")[0]} : ${observationFor(person, phaseIndex())}.`;
    addNote(detail, now);
    state.needs.contact = Math.min(state.needs.contact + 45 * 60 * 1000, now);
    showToast("Vous retenez un détail de plus.");
    render(now);
  }

  function bindEvents() {
    els.selfActions.addEventListener("click", (event) => {
      const button = event.target.closest("[data-action]");
      if (button) doAction(button.dataset.action);
    });
    els.cityMap.addEventListener("click", (event) => {
      const button = event.target.closest("[data-place]");
      if (button) openPlace(button.dataset.place);
    });
    els.residents.addEventListener("click", (event) => {
      const button = event.target.closest("[data-resident]");
      if (button) openResident(button.dataset.resident);
    });
    $("#open-notes").addEventListener("click", openNotes);
    $("#save-bulletin").addEventListener("click", () => { addNote(`Message radio : ${currentPhase().bulletin}`, Date.now()); render(); });
    $("#body-info").addEventListener("click", openBodyInfo);
    $("#open-stash").addEventListener("click", openStash);
    $("#observe-street").addEventListener("click", observeStreet);
    $("#restart-game").addEventListener("click", restart);
    $("#close-modal").addEventListener("click", closeModal);
    els.modalBackdrop.addEventListener("click", (event) => { if (event.target === els.modalBackdrop) closeModal(); });
    els.modalContent.addEventListener("click", (event) => {
      const buy = event.target.closest("[data-buy]");
      if (buy) {
        const [shop, item] = buy.dataset.buy.split(":");
        purchase(shop, item);
      }
      const action = event.target.closest("[data-modal-action]");
      if (!action) return;
      if (action.dataset.modalAction === "restart") {
        localStorage.removeItem(STORAGE_KEY);
        state = createInitialState();
        closeModal(); render(); showToast("Nouvelle chronique commencée.");
      }
      if (action.dataset.modalAction === "observe-square") {
        state.needs.contact = Date.now();
        addNote("Vous êtes restée quelques minutes sur la place. Les gens passent sans se regarder.", Date.now());
        closeModal(); render();
      }
    });
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !els.modalBackdrop.hidden) closeModal(); });
  }

  bindEvents();
  render();
  setInterval(() => render(), 30 * 1000);
})();
