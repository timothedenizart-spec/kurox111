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
    this.addEvent("La montre est réglée. Les informations parlent d’incidents isolés dans plusieurs quartiers.", "world");
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
    const hours = this.player.location === "apartment" ? 7 : 3;
    this.advance(hours * 60, this.player.location === "apartment" ? "Tu dors d’un sommeil léger" : "Tu t’assoupis sans vraiment te sentir en sécurité");
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
      nearby,
      events: [...this.events],
      prices: this.getPrices(),
      marketOpen: this.isMarketOpen(),
    };
  }
}
