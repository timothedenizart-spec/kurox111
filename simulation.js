export const LOCATIONS = [
  {
    id: "apartment",
    name: "Appartement 12",
    description: "Un deux-pièces au troisième étage. La radio grésille derrière la cloison.",
  },
  {
    id: "street",
    name: "Rue des Tilleuls",
    description: "L’axe qui relie les immeubles, le marché et l’atelier municipal.",
  },
  {
    id: "market",
    name: "Marché Cédre",
    description: "Des étals modestes, des prix qui changent et des commerçants fatigués.",
  },
  {
    id: "workshop",
    name: "Atelier municipal",
    description: "Un dépôt de maintenance où le travail rémunéré existe encore au début de la crise.",
  },
  {
    id: "clinic",
    name: "Dispensaire de quartier",
    description: "Un lieu de soin sous pression, bientôt fermé au public.",
  },
  {
    id: "hall",
    name: "Maison de quartier",
    description: "Un ancien lieu d’entraide et d’information qui devient un point de rumeurs.",
  },
];

const HOURS_PER_DAY = 24;
const MINUTES_PER_DAY = HOURS_PER_DAY * 60;

export const PHASES = [
  {
    index: 0,
    fromDay: 1,
    toDay: 2,
    title: "Signaux faibles",
    summary: "Des absences au travail, des rumeurs et quelques files inhabituelles. La monnaie et les services fonctionnent encore.",
    priceFactor: 1,
    marketDays: true,
    workAvailable: true,
  },
  {
    index: 1,
    fromDay: 3,
    toDay: 4,
    title: "Alerte locale",
    summary: "La ville parle d’une maladie inconnue. Les habitants modifient leurs trajets, les prix montent et les premiers commerces limitent leurs horaires.",
    priceFactor: 1.35,
    marketDays: true,
    workAvailable: true,
  },
  {
    index: 2,
    fromDay: 5,
    toDay: 6,
    title: "Rupture des services",
    summary: "Les livraisons se raréfient. Les services publics fonctionnent par intermittence et les habitants privilégient leurs proches.",
    priceFactor: 2.25,
    marketDays: false,
    workAvailable: true,
  },
  {
    index: 3,
    fromDay: 7,
    toDay: 8,
    title: "Basculement",
    summary: "La cohérence sociale se fissure. Les derniers commerces cessent d’échanger normalement et des comportements inquiétants apparaissent la nuit.",
    priceFactor: 5,
    marketDays: false,
    workAvailable: false,
  },
  {
    index: 4,
    fromDay: 9,
    toDay: Number.POSITIVE_INFINITY,
    title: "Après le basculement",
    summary: "La maladie fictive a pris une forme agressive. L’argent ne protège plus : l’abri, l’eau, les liens et la discrétion comptent davantage.",
    priceFactor: Number.POSITIVE_INFINITY,
    marketDays: false,
    workAvailable: false,
  },
];

const RADIO_LEADS = [
  {
    title: "Bulletin de quartier",
    description: "La radio locale conseille de noter les horaires des commerces : les changements commencent toujours par les petites habitudes.",
  },
  {
    title: "Fréquence instable",
    description: "Un animateur répète que les messages fiables circulent de porte en porte, bien avant les communiqués officiels.",
  },
  {
    title: "Voix de la maison de quartier",
    description: "Une voix appelle les habitants à se reconnaître, à partager l’information utile et à éviter les promesses impossibles.",
  },
  {
    title: "Émission coupée",
    description: "Entre deux parasites, tu entends seulement : « Préparez un endroit où dormir. Ne comptez pas sur les magasins. »",
  },
  {
    title: "Canal de survivants",
    description: "Un message bref donne rendez-vous à la maison de quartier : les refuges ne s’ouvrent qu’aux visages connus.",
  },
];

const SIGNALS_BY_PHASE = [
  [
    {
      id: "market-delivery",
      title: "Livraison en retard",
      description: "Au Marché Cédre, une commerçante cherche des bras pour ranger une livraison tardive avant l’ouverture.",
      location: "market",
      action: "Aider au déchargement",
      minutes: 60,
      outcome: "credits",
    },
    {
      id: "notice-board",
      title: "Panneau de quartier",
      description: "À la maison de quartier, quelqu’un met à jour la liste des voisins qui peuvent donner un coup de main.",
      location: "hall",
      action: "Inscrire ton aide",
      minutes: 30,
      outcome: "favour",
    },
  ],
  [
    {
      id: "clinic-queue",
      title: "File silencieuse",
      description: "Le dispensaire cherche une personne calme pour orienter les habitants qui attendent sous la pluie.",
      location: "clinic",
      action: "Orienter les arrivants",
      minutes: 45,
      outcome: "favour",
    },
    {
      id: "message-relay",
      title: "Relais de messages",
      description: "Des voisins tentent de vérifier quelles rues ont encore de l’eau et de l’électricité.",
      location: "hall",
      action: "Recouper les nouvelles",
      minutes: 40,
      outcome: "information",
    },
  ],
  [
    {
      id: "water-table",
      title: "Table de distribution",
      description: "Un groupe de voisins organise une petite distribution à la maison de quartier, sans garantie pour demain.",
      location: "hall",
      action: "Tenir la distribution",
      minutes: 50,
      outcome: "water",
    },
    {
      id: "tools-return",
      title: "Boîte à outils partagée",
      description: "L’atelier municipal prête quelques outils à ceux qui veulent renforcer une porte avant la nuit.",
      location: "workshop",
      action: "Trier les outils",
      minutes: 45,
      outcome: "shelter",
    },
  ],
  [
    {
      id: "door-watch",
      title: "Porte à renforcer",
      description: "Ton immeuble résonne de coups sourds. Une heure maintenant peut rendre ton appartement moins vulnérable cette nuit.",
      location: "apartment",
      action: "Renforcer l’entrée",
      minutes: 90,
      outcome: "shelter",
    },
    {
      id: "hall-watch",
      title: "Veille de quartier",
      description: "La maison de quartier cherche des volontaires pour laisser les familles se reposer à tour de rôle.",
      location: "hall",
      action: "Prendre un tour de veille",
      minutes: 60,
      outcome: "favour",
    },
  ],
  [
    {
      id: "refuge-call",
      title: "Signal de refuge",
      description: "La maison de quartier accepte encore quelques personnes connues pour une nuit encadrée.",
      location: "hall",
      action: "Demander une place",
      minutes: 35,
      outcome: "refuge",
      minFavours: 2,
    },
    {
      id: "quiet-room",
      title: "Appartement silencieux",
      description: "Une voisine laisse un message : les appartements préparés deviennent plus sûrs que les couloirs.",
      location: "apartment",
      action: "Préparer l’appartement",
      minutes: 75,
      outcome: "shelter",
    },
  ],
];

const NPC_TEMPLATES = [
  ["Ana", "soignante", "clinic", "apartment"],
  ["Yanis", "livreur", "workshop", "apartment"],
  ["Mila", "boulangère", "market", "apartment"],
  ["Hugo", "agent municipal", "workshop", "apartment"],
  ["Sofia", "étudiante", "hall", "apartment"],
  ["Rachid", "retraité", "hall", "apartment"],
  ["Noor", "commerçante", "market", "apartment"],
  ["Éloi", "infirmier", "clinic", "apartment"],
  ["Jeanne", "médiatrice", "hall", "apartment"],
  ["Léo", "mécanicien", "workshop", "apartment"],
  ["Inès", "serveuse", "market", "apartment"],
  ["Toma", "lycéen", "hall", "apartment"],
];

const STATE_LABELS = {
  well: "semble concentré",
  exposed: "paraît nerveux",
  ill: "semble souffrant",
  altered: "évite le regard et rôde",
};

const INTENT_LABELS = {
  work: "essaie de travailler",
  shelter: "cherche à rentrer",
  water: "cherche de l’eau",
  talk: "cherche des nouvelles",
  help: "propose son aide",
  avoid: "évite les autres",
  rest: "cherche du calme",
};

const RELATION_LABELS = {
  stranger: "ne te connaît pas encore",
  reserved: "reste réservé",
  familiar: "te reconnaît",
  trusted: "te fait confiance",
};

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function formatTime(minuteOfDay) {
  const total = ((Math.floor(minuteOfDay) % MINUTES_PER_DAY) + MINUTES_PER_DAY) % MINUTES_PER_DAY;
  const hours = String(Math.floor(total / 60)).padStart(2, "0");
  const minutes = String(total % 60).padStart(2, "0");
  return `${hours}:${minutes}`;
}

export function formatDuration(hours) {
  if (hours < 1) return `${Math.round(hours * 60)} min`;
  if (Number.isInteger(hours)) return `${hours} h`;
  return `${hours.toFixed(1).replace(".", ",")} h`;
}

export class PandemicSimulation {
  constructor(seed = 24011991) {
    this.initialSeed = seed >>> 0;
    this.reset();
  }

  reset() {
    this.seed = this.initialSeed;
    this.day = 1;
    this.minute = 7 * 60 + 30;
    this.player = {
      location: "apartment",
      money: 42,
      inventory: { water: 3, food: 2, soap: 1, medicine: 0 },
      lastMeal: this.minute - 150,
      lastWater: this.minute - 75,
      lastSleep: this.minute - 15,
      lastWash: this.minute - 15 * 60,
      lastToilet: this.minute - 105,
      lastConversation: this.minute - 5 * 60,
      favours: 0,
      exposures: [],
      shelterSecured: false,
      refugeAccess: false,
      radioDays: [],
      knownLead: null,
    };
    this.npcs = NPC_TEMPLATES.map(([name, role, workplace, home], index) => ({
      id: `npc-${index}`,
      name,
      role,
      workplace,
      home,
      location: index % 3 === 0 ? workplace : home,
      state: index === 8 ? "exposed" : "well",
      exposedAt: index === 8 ? -20 * 60 : null,
      illAt: null,
      intent: index % 2 === 0 ? "work" : "shelter",
      trust: 1,
      knownPlayer: false,
      memories: [],
      lastWater: this.minute - this.randomInt(30, 210),
      lastRest: this.minute - this.randomInt(60, 450),
      lastConversation: this.minute - this.randomInt(60, 600),
    }));
    this.events = [];
    this.eventId = 0;
    this.resolvedSignalKeys = new Set();
    this.activeSignal = this.createNeighborhoodSignal();
    this.addEvent("La montre est réglée. Les informations parlent d’incidents isolés dans plusieurs quartiers.", "world");
    this.addEvent(`Signal du quartier : ${this.activeSignal.title}.`, "world");
    this.addEvent("Tu commences avec un peu d’eau, de nourriture et assez d’argent pour tenir quelques achats.", "player");
    return this;
  }

  get absoluteMinute() {
    return (this.day - 1) * MINUTES_PER_DAY + this.minute;
  }

  random() {
    this.seed = (Math.imul(1664525, this.seed) + 1013904223) >>> 0;
    return this.seed / 4294967296;
  }

  randomInt(min, max) {
    return Math.floor(this.random() * (max - min + 1)) + min;
  }

  getPhase() {
    return PHASES.find((phase) => this.day >= phase.fromDay && this.day <= phase.toDay) ?? PHASES.at(-1);
  }

  createNeighborhoodSignal() {
    const phase = this.getPhase();
    const choices = SIGNALS_BY_PHASE[phase.index];
    const template = choices[(this.day - 1) % choices.length];
    const key = `${phase.index}-${this.day}-${template.id}`;
    return { ...template, key, resolved: this.resolvedSignalKeys?.has(key) ?? false };
  }

  getCurrentSignal() {
    return { ...this.activeSignal, resolved: this.resolvedSignalKeys.has(this.activeSignal.key) };
  }

  getShelterSignal() {
    if (this.player.refugeAccess) return "Un refuge de quartier t’accepte lorsque la maison de quartier reste accessible.";
    if (this.player.shelterSecured) return "Ton appartement est préparé pour la nuit ; les bruits du couloir restent dehors plus facilement.";
    if (this.getPhase().index >= 3) return "Ton appartement reste un abri précaire tant que son entrée n’est pas préparée.";
    return "L’appartement est encore ordinaire, mais tu peux le préparer avant que la ville ne bascule.";
  }

  getLead() {
    if (this.player.knownLead) return this.player.knownLead;
    return {
      title: "Fréquence inconnue",
      description: "À l’appartement ou à la maison de quartier, prendre vingt minutes pour écouter la radio peut révéler une information utile.",
      known: false,
    };
  }

  getLocation(id = this.player.location) {
    return LOCATIONS.find((location) => location.id === id);
  }

  getHour() {
    return this.minute / 60;
  }

  isMarketOpen() {
    const phase = this.getPhase();
    const hour = this.getHour();
    if (phase.index >= 3 || hour < 8 || hour >= 18) return false;
    if (phase.index === 2) return this.day % 2 === 1;
    return true;
  }

  isClinicOpen() {
    if (this.getPhase().index >= 4) return false;
    return this.getHour() >= 8 && this.getHour() < 20;
  }

  getPrices() {
    const phase = this.getPhase();
    if (!Number.isFinite(phase.priceFactor)) return { water: null, food: null };
    return {
      water: Math.ceil(3 * phase.priceFactor),
      food: Math.ceil(5 * phase.priceFactor),
    };
  }

  getNeedSignals() {
    const now = this.absoluteMinute;
    const elapsed = (lastMinute) => Math.max(0, (now - lastMinute) / 60);
    const needs = [
      {
        id: "water",
        label: "Soif",
        elapsed: elapsed(this.player.lastWater),
        mildAt: 2.5,
        strongAt: 5,
        criticalAt: 9,
        mild: "Ta bouche devient sèche.",
        strong: "Tu as du mal à penser à autre chose qu’à boire.",
        critical: "La déshydratation te ralentit dangereusement.",
      },
      {
        id: "food",
        label: "Faim",
        elapsed: elapsed(this.player.lastMeal),
        mildAt: 5.5,
        strongAt: 11,
        criticalAt: 28,
        mild: "Ton ventre se rappelle à toi.",
        strong: "La faim rend tes décisions moins sûres.",
        critical: "Tu n’as plus l’énergie de te déplacer longtemps.",
      },
      {
        id: "sleep",
        label: "Sommeil",
        elapsed: elapsed(this.player.lastSleep),
        mildAt: 14,
        strongAt: 18,
        criticalAt: 26,
        mild: "Tes paupières deviennent lourdes.",
        strong: "Ta concentration se fragmente.",
        critical: "Tu luttes pour rester éveillé.",
      },
      {
        id: "toilet",
        label: "Besoin naturel",
        elapsed: elapsed(this.player.lastToilet),
        mildAt: 3.5,
        strongAt: 5.5,
        criticalAt: 8,
        mild: "Tu cherches instinctivement des toilettes.",
        strong: "L’inconfort devient difficile à ignorer.",
        critical: "Tu dois t’arrêter et trouver un endroit adapté.",
      },
      {
        id: "hygiene",
        label: "Hygiène",
        elapsed: elapsed(this.player.lastWash),
        mildAt: 22,
        strongAt: 42,
        criticalAt: 72,
        mild: "La poussière et la fatigue te collent à la peau.",
        strong: "Tu te sens mal à l’aise près des autres.",
        critical: "Ton état te rend plus visible et moins à l’aise.",
      },
      {
        id: "social",
        label: "Besoin de lien",
        elapsed: elapsed(this.player.lastConversation),
        mildAt: 11,
        strongAt: 20,
        criticalAt: 34,
        mild: "Le silence devient pesant.",
        strong: "Tu as besoin d’entendre une voix fiable.",
        critical: "L’isolement amplifie chaque bruit et chaque doute.",
      },
    ];

    return needs.map((need) => {
      let severity = "calm";
      let message = "Rien de pressant pour le moment.";
      if (need.elapsed >= need.criticalAt) {
        severity = "critical";
        message = need.critical;
      } else if (need.elapsed >= need.strongAt) {
        severity = "strong";
        message = need.strong;
      } else if (need.elapsed >= need.mildAt) {
        severity = "mild";
        message = need.mild;
      }
      return { ...need, severity, message };
    });
  }

  getCondition() {
    const needs = this.getNeedSignals();
    const critical = needs.filter((need) => need.severity === "critical").length;
    const strong = needs.filter((need) => need.severity === "strong").length;
    if (critical > 0) return "Vulnérable";
    if (strong >= 2) return "Éprouvé";
    if (strong === 1) return "Tendu";
    return "Vigilant";
  }

  getNetworkSignal() {
    if (this.player.favours >= 3) return "Un petit réseau sait désormais que tu tiens parole.";
    if (this.player.favours >= 1) return "Quelques voisins se souviennent de ton aide.";
    return "Tu n’as encore aucune faveur à demander au quartier.";
  }

  getExposureSignal() {
    const windowMinutes = 48 * 60;
    const recent = this.player.exposures.filter((minute) => this.absoluteMinute - minute <= windowMinutes).length;
    if (recent >= 3) return "Plusieurs passages denses te poussent à éviter les attroupements.";
    if (recent >= 2) return "Tu gardes en mémoire plusieurs contacts rapprochés.";
    if (recent === 1) return "Un contact récent te rend plus attentif aux mouvements du quartier.";
    return "Aucun contact récent ne te préoccupe particulièrement.";
  }

  getTrustLabel(npc) {
    if (!npc.knownPlayer) return RELATION_LABELS.stranger;
    if (npc.trust >= 3) return RELATION_LABELS.trusted;
    if (npc.trust >= 2) return RELATION_LABELS.familiar;
    return RELATION_LABELS.reserved;
  }

  recordExposure(locationId) {
    const phase = this.getPhase();
    if (phase.index === 0) return false;
    const crowdedPlace = ["market", "hall", "clinic", "street"].includes(locationId);
    const nearbyCount = this.npcs.filter((npc) => npc.location === locationId).length;
    const chance = (crowdedPlace ? 0.08 : 0.025) + phase.index * 0.045 + Math.min(nearbyCount, 5) * 0.018;
    if (this.random() >= chance) return false;

    this.player.exposures.push(this.absoluteMinute);
    this.player.exposures = this.player.exposures.slice(-6);
    this.addEvent("Un passage trop dense te laisse le souvenir d’un contact rapproché. Tu décides d’être plus prudent.", "world");
    return true;
  }

  addEvent(text, type = "world") {
    this.events.unshift({
      id: ++this.eventId,
      day: this.day,
      time: formatTime(this.minute),
      text,
      type,
    });
    this.events = this.events.slice(0, 18);
  }

  advance(minutes, reason = "Le temps passe.") {
    const roundedMinutes = Math.max(0, Math.round(minutes));
    if (!roundedMinutes) return;
    let remaining = roundedMinutes;
    const startingDay = this.day;

    while (remaining > 0) {
      const minutesToHour = 60 - (this.minute % 60);
      const minutesToMidnight = MINUTES_PER_DAY - this.minute;
      const step = Math.min(remaining, minutesToHour, minutesToMidnight);
      this.minute += step;
      remaining -= step;

      if (this.minute >= MINUTES_PER_DAY) {
        this.minute = 0;
        this.day += 1;
        this.onNewDay();
      }

      if (this.minute % 60 === 0 || remaining === 0) this.simulatePopulation();
    }

    if (reason) this.addEvent(`${reason} (${formatDuration(roundedMinutes / 60)}).`, "player");
    if (this.day !== startingDay) this.addEvent(`Jour ${this.day}. ${this.getPhase().summary}`, "world");
  }

  onNewDay() {
    const phase = this.getPhase();
    if (phase.index === 1 && this.day === 3) {
      this.addEvent("Les vitrines affichent leurs premiers horaires réduits. Plusieurs voisins évitent maintenant les poignées de main.", "world");
    }
    if (phase.index === 2 && this.day === 5) {
      this.addEvent("Les livraisons ont cessé sans explication claire. Les prix changent avant même que les étiquettes soient remplacées.", "world");
    }
    if (phase.index === 3 && this.day === 7) {
      this.addEvent("Un dernier rideau métallique tombe sur le marché. La nuit semble plus longue que d’habitude.", "world");
    }
    if (phase.index === 4 && this.day === 9) {
      this.addEvent("Les échanges en argent ne servent presque plus. Les survivants parlent maintenant d’abri, d’eau et de passages sûrs.", "world");
    }
    this.activeSignal = this.createNeighborhoodSignal();
    this.addEvent(`Nouveau signal du quartier : ${this.activeSignal.title}.`, "world");
  }

  simulatePopulation() {
    const phase = this.getPhase();
    const hour = this.getHour();
    const pressure = 0.004 + phase.index * 0.009;

    for (const npc of this.npcs) {
      const now = this.absoluteMinute;
      const waterHours = (now - npc.lastWater) / 60;
      const restHours = (now - npc.lastRest) / 60;

      if (npc.state === "well" && phase.index > 0 && this.random() < pressure * (npc.location === "market" || npc.location === "hall" ? 1.8 : 1)) {
        npc.state = "exposed";
        npc.exposedAt = now;
        npc.intent = "shelter";
        this.addEvent(`${npc.name} interrompt brusquement son trajet et cherche à rentrer.`, "npc");
      }
      if (npc.state === "exposed" && now - npc.exposedAt > 36 * 60 + this.randomInt(0, 18) * 60) {
        npc.state = "ill";
        npc.illAt = now;
        npc.intent = "rest";
      }
      if (npc.state === "ill" && phase.index >= 3 && now - npc.illAt > 30 * 60 && this.random() < 0.08 + phase.index * 0.03) {
        npc.state = "altered";
        npc.intent = "avoid";
        npc.location = "street";
        this.addEvent(`Un voisin que tu reconnais traverse la rue d’une démarche inhabituelle.`, "world");
      }

      if (npc.state === "altered") {
        npc.location = "street";
        continue;
      }
      if (npc.state === "ill") {
        npc.location = this.isClinicOpen() && this.random() < 0.18 ? "clinic" : npc.home;
        npc.intent = "rest";
        continue;
      }
      if (waterHours > 4.5) {
        npc.intent = "water";
        npc.location = phase.index < 3 ? "market" : npc.home;
        npc.lastWater = now - this.randomInt(0, 30);
        continue;
      }
      if (restHours > 16 || hour < 7 || hour >= 22) {
        npc.intent = "rest";
        npc.location = npc.home;
        npc.lastRest = now - this.randomInt(0, 60);
        continue;
      }
      if (phase.index >= 2 && npc.knownPlayer && npc.trust >= 2 && this.random() < 0.36) {
        npc.intent = "help";
        npc.location = "hall";
        continue;
      }
      if (phase.index >= 2 && this.random() < 0.45) {
        npc.intent = this.random() < 0.35 ? "help" : "shelter";
        npc.location = this.random() < 0.15 ? "hall" : npc.home;
        continue;
      }
      if (hour >= 8 && hour < 17) {
        npc.intent = "work";
        npc.location = npc.workplace;
      } else if (hour >= 17 && hour < 20 && phase.index < 2 && this.random() < 0.38) {
        npc.intent = "talk";
        npc.location = "market";
      } else {
        npc.intent = "shelter";
        npc.location = npc.home;
      }
    }
  }

  move(locationId) {
    const location = this.getLocation(locationId);
    if (!location) return { ok: false, message: "Ce lieu n’existe pas dans cette démo." };
    if (location.id === this.player.location) return { ok: false, message: "Tu es déjà ici." };
    this.player.location = location.id;
    this.advance(45, `Tu te rends à ${location.name}`);
    this.recordExposure(location.id);
    return { ok: true, message: location.description };
  }

  wait() {
    this.advance(30, "Tu observes les allées et venues sans attirer l’attention");
    this.recordExposure(this.player.location);
    return { ok: true, message: "Trente minutes d’observation." };
  }

  listenRadio() {
    if (!["apartment", "hall"].includes(this.player.location)) {
      return { ok: false, message: "Tu n’entends aucune fréquence utile depuis cet endroit." };
    }
    if (this.player.radioDays.includes(this.day)) {
      return { ok: false, message: "Tu as déjà écouté les fréquences disponibles aujourd’hui." };
    }

    this.advance(20, "Tu cherches une voix stable entre les parasites de la radio");
    const lead = RADIO_LEADS[this.getPhase().index];
    this.player.radioDays.push(this.day);
    this.player.knownLead = { ...lead, known: true, day: this.day };
    this.addEvent(`Radio : ${lead.description}`, "world");
    return { ok: true, message: "La radio ne donne pas de certitude, mais une piste pour comprendre ce qui change." };
  }

  secureShelter() {
    if (this.player.location !== "apartment") return { ok: false, message: "Tu dois être chez toi pour préparer ton abri." };
    if (this.player.shelterSecured) return { ok: false, message: "L’entrée est déjà préparée pour la nuit." };

    this.advance(90, "Tu bloques les points faibles de l’entrée et ranges l’essentiel près de la porte");
    this.player.shelterSecured = true;
    this.addEvent("Ton appartement n’est pas inviolable, mais il te donne enfin une nuit un peu moins incertaine.", "player");
    return { ok: true, message: "L’appartement devient un abri plus fiable sans transformer la sécurité en jauge." };
  }

  requestRefuge() {
    if (this.player.location !== "hall") return { ok: false, message: "Le refuge se négocie à la maison de quartier." };
    if (this.player.refugeAccess) return { ok: false, message: "Le quartier connaît déjà ton visage et t’accorde une place quand il le peut." };
    if (this.getPhase().index < 2) return { ok: false, message: "Le refuge n’est pas encore organisé. Pour l’instant, les voisins font comme si demain était garanti." };
    if (this.player.favours < 2) return { ok: false, message: "Il faut d’abord créer des liens concrets avant de demander une place dans un refuge rare." };

    this.advance(35, "Tu expliques ce que tu peux apporter au refuge de quartier");
    this.player.refugeAccess = true;
    this.addEvent("Une médiatrice note ton nom à la main. Le refuge n’est pas un droit, mais une porte pourra s’ouvrir.", "npc");
    return { ok: true, message: "Un abri collectif devient une option lorsque la maison de quartier est accessible." };
  }

  resolveSignal() {
    const signal = this.getCurrentSignal();
    if (signal.resolved) return { ok: false, message: "Tu as déjà répondu à ce signal aujourd’hui." };
    if (signal.location !== this.player.location) {
      return { ok: false, message: `Ce signal demande de te rendre à ${this.getLocation(signal.location).name}.` };
    }
    if (signal.minFavours && this.player.favours < signal.minFavours) {
      return { ok: false, message: "Le refuge cherche des visages connus. Aider le quartier d’abord peut ouvrir cette possibilité." };
    }

    this.advance(signal.minutes, signal.action);
    let outcomeMessage;
    switch (signal.outcome) {
      case "credits":
        this.player.money += 8;
        outcomeMessage = "On te donne quelques crédits tant que les échanges ordinaires existent encore.";
        break;
      case "favour":
        this.player.favours = clamp(this.player.favours + 1, 0, 5);
        this.player.lastConversation = this.absoluteMinute;
        outcomeMessage = "Des voisins retiennent ton nom ; l’entraide gagne du terrain.";
        break;
      case "information": {
        const lead = RADIO_LEADS[this.getPhase().index];
        this.player.knownLead = { ...lead, known: true, day: this.day };
        outcomeMessage = "Les témoignages recoupés donnent une piste plus solide que les rumeurs isolées.";
        break;
      }
      case "water":
        this.player.inventory.water += 1;
        this.player.favours = clamp(this.player.favours + 1, 0, 5);
        outcomeMessage = "Après la distribution, une bouteille t’est confiée et ton aide est remarquée.";
        break;
      case "shelter":
        this.player.shelterSecured = true;
        outcomeMessage = "Les outils et le temps partagé rendent ton abri moins précaire pour la nuit.";
        break;
      case "refuge":
        this.player.refugeAccess = true;
        outcomeMessage = "Le quartier reconnaît ce que tu as déjà donné et te réserve une place si les portes restent ouvertes.";
        break;
      default:
        outcomeMessage = "Le quartier garde une trace de ton passage.";
    }

    this.resolvedSignalKeys.add(signal.key);
    this.activeSignal = { ...signal, resolved: true };
    this.addEvent(`${signal.title} : ${outcomeMessage}`, "world");
    return { ok: true, message: outcomeMessage };
  }

  eat() {
    if (this.player.inventory.food < 1) return { ok: false, message: "Il ne reste rien de comestible dans ton sac." };
    this.player.inventory.food -= 1;
    this.advance(20, "Tu manges lentement pour économiser tes forces");
    this.player.lastMeal = this.absoluteMinute;
    return { ok: true, message: "La faim recule pour un moment." };
  }

  drink() {
    if (this.player.inventory.water < 1) return { ok: false, message: "Tu n’as plus d’eau potable." };
    this.player.inventory.water -= 1;
    this.advance(10, "Tu bois quelques gorgées");
    this.player.lastWater = this.absoluteMinute;
    return { ok: true, message: "Tu reprends un peu de clarté." };
  }

  sleep() {
    const atApartment = this.player.location === "apartment";
    const atRefuge = this.player.location === "hall" && this.player.refugeAccess;
    const hours = atApartment ? (this.player.shelterSecured || this.getPhase().index < 3 ? 7 : 5) : atRefuge ? 6 : 3;
    const reason = atApartment
      ? this.player.shelterSecured
        ? "Tu dors derrière une entrée préparée, sans jamais oublier le couloir"
        : "Tu dors d’un sommeil léger, attentif aux bruits de l’immeuble"
      : atRefuge
        ? "Tu te reposes à tour de rôle parmi des voisins qui veillent"
        : "Tu t’assoupis sans vraiment te sentir en sécurité";
    this.advance(hours * 60, reason);
    this.player.lastSleep = this.absoluteMinute;
    return { ok: true, message: "Tu te réveilles avec une perception plus nette du quartier." };
  }

  wash() {
    if (this.player.location !== "apartment" && this.player.location !== "clinic") {
      return { ok: false, message: "Tu ne trouves ni eau ni intimité suffisantes ici." };
    }
    if (this.player.inventory.soap < 1 && this.player.location === "apartment") {
      return { ok: false, message: "Tu n’as plus de savon à la maison." };
    }
    this.advance(20, "Tu prends le temps de te nettoyer");
    this.player.lastWash = this.absoluteMinute;
    if (this.player.location === "apartment") this.player.inventory.soap = Math.max(0, this.player.inventory.soap - 1);
    return { ok: true, message: "Tu te sens moins exposé et plus présentable." };
  }

  useToilet() {
    if (!["apartment", "clinic", "hall"].includes(this.player.location)) {
      return { ok: false, message: "Aucun lieu discret et utilisable à proximité." };
    }
    this.advance(8, "Tu t’éclipses quelques instants");
    this.player.lastToilet = this.absoluteMinute;
    return { ok: true, message: "Tu peux reprendre la route plus sereinement." };
  }

  talk() {
    const nearby = this.getNearbyNpcs();
    if (!nearby.length) return { ok: false, message: "Personne ne reste assez longtemps pour parler." };
    const npc = nearby[0];
    const phase = this.getPhase();
    this.advance(25, `Tu échanges quelques mots avec ${npc.name}`);
    this.player.lastConversation = this.absoluteMinute;
    npc.knownPlayer = true;
    npc.trust = clamp(npc.trust + 1, 0, 3);
    npc.memories.push({ kind: "conversation", at: this.absoluteMinute });
    npc.memories = npc.memories.slice(-3);
    const rumoursByPhase = [
      [
        "Les livraisons de la périphérie arrivent de moins en moins souvent.",
        "Les prix ont encore changé ce matin, avant l’ouverture des étals.",
      ],
      [
        "Des voisins notent quels immeubles restent éclairés après minuit.",
        "Le dispensaire trie les arrivées avant même d’ouvrir sa porte.",
      ],
      [
        "La maison de quartier garde une réserve, mais seulement pour les gens connus.",
        "Certains habitants échangent déjà une bouteille contre un service, sans parler de crédits.",
      ],
      [
        "Les gens qui restent dehors après le coucher du soleil ne rentrent pas toujours seuls.",
        "La rue est devenue plus silencieuse que les appartements.",
      ],
      [
        "Les portes s’ouvrent rarement pour un inconnu, mais les services rendus se racontent.",
        "On ne parle plus de prix : on parle de ce que chacun peut apporter au refuge.",
      ],
    ];
    const rumours = rumoursByPhase[phase.index];
    const message = rumours[this.randomInt(0, rumours.length - 1)];
    this.addEvent(`${npc.name} : « ${message} »`, "npc");
    if (["market", "hall", "clinic"].includes(this.player.location)) this.recordExposure(this.player.location);
    return { ok: true, message: `${npc.name} te reconnaîtra plus facilement lors d’une prochaine rencontre.` };
  }

  share(item) {
    if (!["water", "food"].includes(item)) return { ok: false, message: "Tu ne peux partager que de l’eau ou de la nourriture." };
    if (this.player.inventory[item] < 1) return { ok: false, message: `Tu n’as plus ${item === "water" ? "d’eau" : "de nourriture"} à offrir.` };
    const npc = this.getNearbyNpcs()[0];
    if (!npc) return { ok: false, message: "Personne ne peut recevoir cette aide ici." };

    this.player.inventory[item] -= 1;
    this.advance(15, `Tu offres ${item === "water" ? "de l’eau" : "de la nourriture"} à ${npc.name}`);
    this.player.lastConversation = this.absoluteMinute;
    this.player.favours = clamp(this.player.favours + 1, 0, 5);
    npc.knownPlayer = true;
    npc.trust = clamp(npc.trust + 2, 0, 3);
    npc.memories.push({ kind: `shared-${item}`, at: this.absoluteMinute });
    npc.memories = npc.memories.slice(-3);
    this.addEvent(`${npc.name} garde le geste en mémoire. Dans ce quartier, l’entraide vaut bientôt plus qu’un billet.`, "npc");
    return { ok: true, message: "Un lien de confiance se crée, sans qu’aucun chiffre ne soit affiché." };
  }

  requestAid() {
    const npc = this.getNearbyNpcs().find((resident) => resident.knownPlayer && resident.trust >= 2);
    if (!npc) return { ok: false, message: "Personne ici ne te connaît assez pour puiser dans ses propres réserves." };
    if (this.player.favours < 1) return { ok: false, message: "Tu n’as encore aucune faveur à demander au quartier." };
    if (this.getPhase().index < 2) return { ok: false, message: "Pour l’instant, les échanges ordinaires fonctionnent encore. Le réseau d’entraide n’est pas prêt." };

    const item = this.player.inventory.water < 1 ? "water" : "food";
    this.advance(15, `${npc.name} vérifie discrètement ce qu’il peut partager`);
    this.player.inventory[item] += 1;
    this.player.favours = Math.max(0, this.player.favours - 1);
    this.player.lastConversation = this.absoluteMinute;
    this.addEvent(`${npc.name} t’aide sans demander de crédits en retour.`, "npc");
    return { ok: true, message: `${npc.name} te confie ${item === "water" ? "de l’eau" : "de la nourriture"}. Le réseau prend le relais de l’argent.` };
  }

  work() {
    if (this.player.location !== "workshop") return { ok: false, message: "Le seul travail déclaré de la démo se trouve à l’atelier municipal." };
    if (!this.getPhase().workAvailable) return { ok: false, message: "L’atelier est abandonné. Personne ne paie plus le travail déclaré." };
    const pay = this.getPhase().index === 0 ? 14 : this.getPhase().index === 1 ? 11 : 7;
    this.advance(4 * 60, "Tu aides à maintenir des équipements dont personne ne sait encore s’ils serviront demain");
    this.player.money += pay;
    this.addEvent(`On te remet ${pay} crédits pour ta journée.`, "player");
    return { ok: true, message: `Tu gagnes ${pay} crédits, mais la journée a coûté du temps et de l’énergie.` };
  }

  buy(item) {
    if (this.player.location !== "market") return { ok: false, message: "Il faut être au Marché Cédre pour acheter." };
    if (!this.isMarketOpen()) return { ok: false, message: "Le marché est fermé, vidé ou trop dangereux pour échanger." };
    const prices = this.getPrices();
    const cost = prices[item];
    if (!cost) return { ok: false, message: "Cet échange n’est plus possible." };
    if (this.player.money < cost) return { ok: false, message: "Tu n’as pas assez de crédits." };
    this.player.money -= cost;
    this.player.inventory[item] += 1;
    this.advance(12, `Tu négocies l’achat d’une unité de ${item === "water" ? "d’eau" : "nourriture"}`);
    return { ok: true, message: `Tu échanges ${cost} crédits contre ${item === "water" ? "de l’eau" : "de la nourriture"}.` };
  }

  getNearbyNpcs() {
    return this.npcs.filter((npc) => npc.location === this.player.location && npc.state !== "altered");
  }

  getPopulationSummary() {
    const summary = { well: 0, exposed: 0, ill: 0, altered: 0 };
    for (const npc of this.npcs) summary[npc.state] += 1;
    return summary;
  }

  getWorldSignals() {
    const phase = this.getPhase();
    const population = this.getPopulationSummary();
    const market = this.isMarketOpen() ? "ouvert" : phase.index >= 3 ? "abandonné" : "fermé pour le moment";
    const currency = phase.index < 2 ? "Les crédits sont encore acceptés." : phase.index < 4 ? "Les crédits ne suffisent plus toujours à convaincre." : "Les crédits n’ont presque plus de valeur pratique.";
    return {
      phase,
      population,
      market,
      currency,
      network: this.getNetworkSignal(),
      exposure: this.getExposureSignal(),
      shelter: this.getShelterSignal(),
      clinic: this.isClinicOpen() ? "Le dispensaire reçoit encore du monde." : "Le dispensaire est fermé ou inaccessible.",
    };
  }

  getSnapshot() {
    const location = this.getLocation();
    const nearby = this.getNearbyNpcs().map((npc) => ({
      name: npc.name,
      role: npc.role,
      state: STATE_LABELS[npc.state],
      intent: INTENT_LABELS[npc.intent],
      relation: this.getTrustLabel(npc),
    }));
    return {
      day: this.day,
      time: formatTime(this.minute),
      location,
      condition: this.getCondition(),
      player: structuredClone(this.player),
      needs: this.getNeedSignals(),
      phase: this.getPhase(),
      world: this.getWorldSignals(),
      signal: this.getCurrentSignal(),
      lead: this.getLead(),
      nearby,
      events: [...this.events],
      prices: this.getPrices(),
      marketOpen: this.isMarketOpen(),
    };
  }
}
