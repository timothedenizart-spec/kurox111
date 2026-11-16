(() => {
  'use strict';

  const SAVE_KEY = 'veille-save-v1';
  const DAY_NAMES = ['MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE', 'LUNDI'];
  const ITEMS = {
    water: { label: 'Bouteille d’eau', short: 'Eau', icon: '◒', price: 4 },
    ration: { label: 'Repas emballé', short: 'Repas', icon: '◇', price: 8 },
    mask: { label: 'Masque filtrant', short: 'Masque', icon: '▱', price: 11 },
    soap: { label: 'Savon', short: 'Savon', icon: '▧', price: 5 },
    medkit: { label: 'Trousse de secours', short: 'Trousse', icon: '✚', price: 18 },
  };
  const LOCATIONS = {
    home: {
      name: 'Appartement, rue des Goélands', short: 'Chez vous', icon: '⌂',
      detail: 'Un endroit familier, encore à l’abri du bruit de la rue.', risk: 0.002, distance: 0,
      scene: 'Le radiateur claque doucement. Par la fenêtre entrouverte, la rue semble presque ordinaire. Sur la table, la radio grésille entre deux bulletins.'
    },
    market: {
      name: 'Épicerie du Port', short: 'Épicerie', icon: '▤',
      detail: 'Le rideau est levé pour le moment.', risk: 0.032, distance: 18,
      scene: 'La lumière blanche des néons ne parvient pas à rendre l’endroit accueillant. Une file s’étire devant le comptoir; les conversations s’interrompent quand la porte s’ouvre.'
    },
    clinic: {
      name: 'Centre médical', short: 'Dispensaire', icon: '✚',
      detail: 'Une odeur de désinfectant flotte jusque dans le couloir.', risk: 0.052, distance: 24,
      scene: 'Des chaises ont été espacées dans la salle d’attente. Une infirmière note des noms sur un carnet, sans lever les yeux.'
    },
    townhall: {
      name: 'Place de la Mairie', short: 'Mairie', icon: '▦',
      detail: 'Des affiches fraîches recouvrent les anciennes.', risk: 0.026, distance: 21,
      scene: 'Quelques habitants se tiennent à distance sous l’auvent. Un haut-parleur diffuse des consignes que le vent emporte par morceaux.'
    },
    depot: {
      name: 'Dépôt des cars · sortie nord', short: 'Dépôt des cars', icon: '▣',
      detail: 'Les cars attendent, moteurs froids.', risk: 0.023, distance: 34,
      scene: 'Des barrières improvisées barrent une partie du quai. Les horaires affichés ont été corrigés à la main, puis arrachés.'
    },
    square: {
      name: 'Square des Tilleuls', short: 'Square', icon: '♧',
      detail: 'Les allées sont presque désertes.', risk: 0.012, distance: 14,
      scene: 'La bruine perle sur les bancs. Des papiers roulent contre la grille; au loin, les cloches sonnent avec quelques minutes de retard.'
    },
  };

  const PHASES = [
    { from: 1, key: 'first', label: 'Des cas inexpliqués', indicator: 'INQUIÉTANTE', risk: 1, copy: 'Les autorités parlent de cas isolés. Le centre médical demande aux personnes fiévreuses d’éviter les salles d’attente bondées.' },
    { from: 2, key: 'reports', label: 'Les signalements se multiplient', indicator: 'SOUS SURVEILLANCE', risk: 1.25, copy: 'Des consultations inhabituelles sont signalées dans plusieurs communes. Les informations restent fragmentaires; les commerces sont ouverts.' },
    { from: 4, key: 'alert', label: 'Les premiers services débordent', indicator: 'ALERTE LOCALE', risk: 1.55, copy: 'Des files se forment devant les pharmacies et le dispensaire. Les horaires changent sans préavis et les messages officiels se contredisent.' },
    { from: 7, key: 'emergency', label: 'La ville se replie', indicator: 'URGENCE', risk: 1.9, copy: 'Plusieurs services tournent au ralenti. Les déplacements sont déconseillés; les habitants s’organisent par petits groupes.' },
    { from: 11, key: 'mutation', label: 'Des symptômes inhabituels', indicator: 'CRISE', risk: 2.25, copy: 'Les bulletins évoquent des troubles neurologiques et des réactions inattendues chez certains malades. Les soignants réclament du renfort.' },
    { from: 16, key: 'reanimation', label: 'La nuit a changé de visage', indicator: 'RUPTURE', risk: 2.7, copy: 'Des témoins parlent de personnes qui se relèvent après s’être effondrées. Les mots officiels ont disparu; les rues se vident.' },
  ];

  const PEOPLE = [
    { id: 'lila', name: 'Lila Ben Amar', role: 'Voisine · connaît tout le quartier', initial: 'L', startLocation: 'home' },
    { id: 'yann', name: 'Yann Morel', role: 'Épicier · garde la boutique', initial: 'Y', startLocation: 'market' },
    { id: 'mina', name: 'Mina Le Guen', role: 'Infirmière · centre médical', initial: 'M', startLocation: 'clinic' },
  ];

  function freshState() {
    const abs = 7 * 60 + 20;
    return {
      version: 1,
      absMin: abs,
      current: 'home',
      selected: null,
      money: 38,
      inventory: { water: 2, ration: 2, mask: 1, soap: 1, medkit: 0 },
      body: {
        lastDrink: abs - 95,
        lastEat: abs - 250,
        awakeHours: 1.8,
        lastToilet: abs - 145,
        lastBowel: abs - 8 * 60,
        lastWash: abs - 11 * 60,
        condition: 100,
      },
      maskUntil: 0,
      infection: null,
      world: {
        processedDay: 1,
        activeCases: 31,
        cumulativeCases: 54,
        deaths: 2,
        marketStock: { water: 15, ration: 12, mask: 6, soap: 5, medkit: 2 },
        clinicOpen: true,
        power: true,
        waterService: true,
        workedDays: [],
        convoyAnnounced: false,
        outbreakName: 'La fièvre de Penmarch',
      },
      people: {
        lila: { location: 'home', trust: 0, trustDay: 0, favorDay: 0, met: false, infectionAt: null, sick: false, safe: true },
        yann: { location: 'market', trust: 0, trustDay: 0, favorDay: 0, met: false, infectionAt: null, sick: false, safe: true },
        mina: { location: 'clinic', trust: 0, trustDay: 0, favorDay: 0, met: false, infectionAt: null, sick: false, safe: true },
      },
      log: [
        { time: '07:20', text: 'La radio locale signale plusieurs cas de fièvre dans le secteur.', type: 'important' },
        { time: '07:20', text: 'Mina, du centre médical, demande aux habitants de téléphoner avant de se déplacer.', type: '' },
      ],
      ended: null,
    };
  }

  let state = loadState();
  let toastTimer = null;

  function loadState() {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) return freshState();
      const saved = JSON.parse(raw);
      if (!saved || saved.version !== 1 || !saved.body || !saved.world) return freshState();
      return saved;
    } catch (_) {
      return freshState();
    }
  }

  function saveState() {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); } catch (_) { /* mode privé ou stockage indisponible */ }
  }

  const dayNumber = () => Math.floor(state.absMin / 1440) + 1;
  const minuteOfDay = () => ((state.absMin % 1440) + 1440) % 1440;
  const hourOfDay = () => Math.floor(minuteOfDay() / 60);
  const clockText = () => `${String(hourOfDay()).padStart(2, '0')}:${String(minuteOfDay() % 60).padStart(2, '0')}`;
  const elapsedHours = (stamp) => Math.max(0, (state.absMin - stamp) / 60);
  const phaseForDay = (day = dayNumber()) => [...PHASES].reverse().find(p => day >= p.from) || PHASES[0];
  const moneyText = (amount) => `${Math.max(0, Math.floor(amount))} €`;
  const plural = (n, singular, pluralForm = `${singular}s`) => n > 1 ? pluralForm : singular;

  function addLog(text, type = '') {
    state.log.unshift({ time: clockText(), text, type });
    state.log = state.log.slice(0, 24);
  }

  function notify(text) {
    const toast = document.getElementById('toast');
    toast.textContent = text;
    toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2400);
  }

  function marketLevel(day = dayNumber()) {
    if (day <= 2) return { key: 'open', label: 'Ouvert', detail: 'Le rideau est levé pour le moment.', saleFactor: 1 };
    if (day <= 5) return { key: 'limited', label: 'Horaires réduits', detail: 'La boutique ferme plus tôt; les rayons se vident.', saleFactor: 1.25 };
    if (day <= 8) return { key: 'rationed', label: 'Accès rationné', detail: 'Une file est organisée dehors; certains produits sont limités.', saleFactor: 1.7 };
    return { key: 'closed', label: 'Fermé', detail: 'La boutique a baissé son rideau. Les étagères visibles sont presque nues.', saleFactor: 0 };
  }

  function locationAvailability(key) {
    const day = dayNumber();
    if (key === 'market') return marketLevel().detail;
    if (key === 'clinic') {
      if (day >= 13) return 'Équipe réduite · accès incertain';
      if (day >= 8) return 'Urgences uniquement';
      return 'Un service reste assuré';
    }
    if (key === 'depot') return state.world.convoyAnnounced ? 'Un rassemblement est annoncé' : 'Les horaires ont été suspendus';
    if (key === 'townhall' && day >= 9) return 'Point de rassemblement improvisé';
    if (key === 'square' && day >= 12) return 'Évitez les lieux découverts';
    return LOCATIONS[key].detail;
  }

  function needDescriptor(hours, thresholds, lines) {
    let tier = 0;
    for (let i = 0; i < thresholds.length; i++) if (hours >= thresholds[i]) tier = i + 1;
    return { tier, text: lines[Math.min(tier, lines.length - 1)] };
  }

  function needs() {
    const b = state.body;
    return [
      { key: 'thirst', icon: '◒', title: 'Soif', ...needDescriptor(elapsedHours(b.lastDrink), [1.5, 3, 5, 8], ['Vous n’y pensez pas encore.', 'La bouche commence à sécher.', 'Vous cherchez instinctivement quelque chose à boire.', 'La soif vous déconcentre; il faudrait boire bientôt.', 'La déshydratation devient dangereuse.']) },
      { key: 'hunger', icon: '◇', title: 'Faim', ...needDescriptor(elapsedHours(b.lastEat), [3, 6, 10, 17], ['Votre estomac est calme.', 'Un creux se fait sentir.', 'Vous avez du mal à penser à autre chose qu’à manger.', 'La faiblesse commence à ralentir vos gestes.', 'Votre corps manque sérieusement d’énergie.']) },
      { key: 'sleep', icon: '☾', title: 'Sommeil', ...needDescriptor(b.awakeHours, [10, 14, 18, 25], ['Vous êtes reposé.', 'Vos yeux piquent un peu.', 'La concentration vous échappe par moments.', 'Chaque effort demande plus de volonté.', 'Vous risquez de vous assoupir sans le vouloir.']) },
      { key: 'bladder', icon: '⌁', title: 'Besoin naturel', ...needDescriptor(elapsedHours(b.lastToilet), [2.5, 4, 6, 9], ['Aucun besoin pressant.', 'Vous sentez une légère envie.', 'Vous commencez à chercher des toilettes.', 'L’inconfort devient difficile à ignorer.', 'Il faut trouver des toilettes sans tarder.']) },
      { key: 'bowel', icon: '⌖', title: 'Transit', ...needDescriptor(elapsedHours(b.lastBowel), [12, 24, 36, 48], ['Rien à signaler.', 'Un besoin naturel se fait attendre.', 'Vous devriez prévoir un passage aux toilettes.', 'L’inconfort vous préoccupe.', 'Le besoin devient très pressant.']) },
      { key: 'hygiene', icon: '✳', title: 'Hygiène', ...needDescriptor(elapsedHours(b.lastWash), [18, 30, 48, 72], ['Vous êtes propre.', 'Vous vous sentez un peu défraîchi.', 'La poussière et la sueur vous collent à la peau.', 'Vous aimeriez vraiment pouvoir vous laver.', 'L’hygiène devient un problème pour votre confort.']) },
    ];
  }

  function marketPrice(itemKey) {
    const base = ITEMS[itemKey].price;
    const pressure = 1 + Math.max(0, dayNumber() - 1) * 0.12;
    const stockFactor = marketLevel().saleFactor || 1;
    return Math.ceil(base * pressure * stockFactor);
  }

  function travelMinutes(from, to) {
    if (from === to) return 0;
    const distances = {
      home: { market: 18, clinic: 23, townhall: 20, depot: 34, square: 14 },
      market: { clinic: 18, townhall: 13, depot: 27, square: 12 },
      clinic: { townhall: 16, depot: 25, square: 19 },
      townhall: { depot: 20, square: 10 },
      depot: { square: 26 },
    };
    return distances[from]?.[to] ?? distances[to]?.[from] ?? 20;
  }

  function exposedAt(locationKey, isTravel = false) {
    const location = LOCATIONS[locationKey];
    if (!location || !location.risk) return 0.003;
    const travelModifier = isTravel ? 0.55 : 1;
    const localRisk = location.risk * phaseForDay().risk;
    const contactRisk = PEOPLE.reduce((risk, person) => {
      const contact = state.people[person.id];
      if (!contact || !contact.safe || contact.location !== locationKey) return risk;
      if (contact.sick) return risk + 0.055;
      if (contact.infectionAt) return risk + 0.012;
      return risk;
    }, 0);
    return Math.min(0.2, localRisk + contactRisk) * travelModifier;
  }

  function maybeExposePlayer(locationKey, sleeping = false, isTravel = false, elapsedHours = 0.25) {
    if (sleeping || state.infection) return;
    let risk = exposedAt(locationKey, isTravel) * elapsedHours;
    if (state.maskUntil > state.absMin) risk *= 0.2;
    if (Math.random() < risk) {
      state.infection = { exposedAt: state.absMin, symptomatic: false, severity: 0, strain: 'initial' };
      addLog('Vous avez passé du temps près d’une personne qui toussait. Vous ne savez pas si vous avez été exposé.', 'important');
      notify('Une exposition possible. Surveillez les signes dans les prochains jours.');
    }
  }

  function currentInfectionHours() {
    return state.infection ? (state.absMin - state.infection.exposedAt) / 60 : 0;
  }

  function updateInfectionHourly() {
    if (!state.infection) return;
    const hours = currentInfectionHours();
    const day = dayNumber();
    if (day >= 11) state.infection.strain = 'mutating';
    if (day >= 16) state.infection.strain = 'late';
    if (hours >= 48) {
      state.infection.symptomatic = true;
      const stageFactor = day >= 16 ? 2.2 : day >= 11 ? 1.5 : 1;
      state.infection.severity = Math.min(100, state.infection.severity + 0.8 * stageFactor);
      if (Math.floor(state.infection.severity) % 15 === 0 && state.infection.severity > 0) {
        addLog(state.infection.strain === 'late' ? 'La fièvre cède parfois la place à une agitation inquiétante.' : 'La fièvre monte; vos pensées deviennent plus lentes.', 'danger');
      }
      if (state.infection.severity > 68) state.body.condition = Math.max(0, state.body.condition - 0.45 * stageFactor);
      if (state.infection.severity >= 100 && state.infection.strain === 'late') {
        endGame('Vous n’êtes plus vous-même', 'La maladie a achevé sa dernière transformation. Vos souvenirs s’éloignent tandis que la ville devient un monde de silhouettes errantes.');
      }
    }
  }

  function updateNpcHourly() {
    const day = dayNumber();
    const hour = hourOfDay();
    const phase = phaseForDay(day);
    for (const person of PEOPLE) {
      const data = state.people[person.id];
      if (!data || !data.safe) continue;
      if (data.infectionAt && !data.sick && state.absMin - data.infectionAt > 48 * 60) {
        data.sick = true;
        addLog(`${person.name} ne s’est pas présenté${person.id === 'mina' ? 'e' : ''} comme prévu.`, 'important');
      }
      if (data.sick) {
        data.location = 'home';
        data.goal = 's’isoler et protéger ses proches';
      } else if (person.id === 'lila') {
        data.location = day >= 8 && hour >= 8 && hour < 19 ? 'townhall' : (hour >= 8 && hour < 18 && day < 8 ? 'square' : 'home');
        data.goal = day >= 8 ? 'retrouver sa sœur et organiser le voisinage' : 'prendre des nouvelles du quartier';
      } else if (person.id === 'yann') {
        data.location = day <= 8 && hour >= 7 && hour < 19 ? 'market' : (hour >= 20 || hour < 7 ? 'home' : 'townhall');
        data.goal = day <= 5 ? 'garder la boutique ouverte' : day <= 8 ? 'répartir les dernières réserves' : 'protéger ses proches';
      } else {
        data.location = day <= 12 && hour >= 7 && hour < 20 ? 'clinic' : (day >= 13 && hour >= 9 && hour < 18 ? 'townhall' : 'home');
        data.goal = day <= 8 ? 'maintenir le dispensaire' : day <= 15 ? 'soigner sans matériel' : 'mettre les survivants à l’abri';
      }
      const npcRisk = exposedAt(data.location) * (data.safe ? 0.22 : 0.85);
      if (!data.infectionAt && Math.random() < npcRisk) data.infectionAt = state.absMin;
      if (phase.key === 'reanimation' && data.sick && state.absMin - data.infectionAt > 6 * 1440) {
        data.safe = false;
        addLog(`Plus personne n’a vu ${person.name} depuis la nuit dernière. Dans le quartier, on évite de parler de ce qui a pu se passer.`, 'danger');
      }
    }
  }

  function applyNeedConsequences() {
    const b = state.body;
    const thirst = elapsedHours(b.lastDrink);
    const hunger = elapsedHours(b.lastEat);
    const bladder = elapsedHours(b.lastToilet);
    const bowel = elapsedHours(b.lastBowel);
    const awake = b.awakeHours;
    if (thirst > 10) b.condition -= 0.6;
    if (hunger > 25) b.condition -= 0.22;
    if (awake > 22) b.condition -= 0.14;
    if (bladder > 11) b.condition -= 0.12;
    if (bowel > 56) b.condition -= 0.06;
    b.condition = Math.max(0, Math.min(100, b.condition));
    if (b.condition <= 0 && !state.ended) endGame('Vous vous effondrez', 'Votre corps a fini par céder. Les petits signes que vous aviez repoussés sont devenus impossibles à ignorer.');
  }

  function updateWorldDay(day) {
    const previous = state.world.processedDay;
    state.world.processedDay = day;
    const growth = day < 4 ? 1.5 : day < 8 ? 1.8 : day < 12 ? 1.55 : 1.35;
    const added = Math.max(5, Math.round(state.world.activeCases * (growth - 1)));
    state.world.activeCases += added;
    state.world.cumulativeCases += added + Math.round(added * 0.45);
    state.world.deaths += Math.max(1, Math.round(added * (day < 8 ? 0.07 : day < 16 ? 0.13 : 0.2)));
    for (const key of Object.keys(state.world.marketStock)) {
      const remaining = state.world.marketStock[key];
      if (remaining > 0) state.world.marketStock[key] = Math.max(0, remaining - (key === 'water' || key === 'ration' ? (day < 5 ? 2 : 3) : 1));
    }
    if (day >= 8) state.world.clinicOpen = false;
    if (day >= 9) state.world.power = false;
    if (day >= 11) state.world.waterService = false;
    if (day >= 12 && !state.world.convoyAnnounced) {
      state.world.convoyAnnounced = true;
      addLog('À la radio, une voix annonce un convoi d’évacuation au dépôt des cars, à partir du jour 18. L’information n’est pas confirmée.', 'important');
    }
    if (day > previous) {
      addLog(`Un nouveau jour se lève. Les commerces et les services ouvrent moins régulièrement.`, 'important');
      const phase = phaseForDay(day);
      if (phase.from === day) addLog(`Bulletin radio : « ${phase.label}. »`, 'danger');
      if (day === 4) addLog('L’épicerie annonce des horaires réduits et une hausse des prix.', 'important');
      if (day === 7) addLog('La mairie appelle les habitants à limiter les déplacements.', 'important');
      if (day === 9) addLog('Des coupures de courant touchent plusieurs rues.', 'important');
      if (day === 11) addLog('L’eau courante est coupée dans une partie du quartier.', 'important');
      if (day === 16) addLog('La radio cesse d’émettre des bulletins réguliers. Des bruits circulent dans les rues désertes.', 'danger');
    }
  }

  function advanceTime(minutes, options = {}) {
    if (state.ended) return;
    const startDay = dayNumber();
    const wasSleeping = Boolean(options.sleeping);
    const riskLocation = options.riskLocation || state.current;
    let remaining = minutes;
    while (remaining > 0 && !state.ended) {
      const step = Math.min(15, remaining);
      state.absMin += step;
      remaining -= step;
      if (!wasSleeping) state.body.awakeHours += step / 60;
      maybeExposePlayer(riskLocation, wasSleeping, Boolean(options.isTravel), step / 60);
      if (Math.floor(minuteOfDay() / 60) !== Math.floor(((minuteOfDay() - step + 1440) % 1440) / 60)) {
        updateInfectionHourly();
        updateNpcHourly();
        applyNeedConsequences();
      }
      const day = dayNumber();
      if (day > state.world.processedDay) updateWorldDay(day);
    }
    if (wasSleeping && !state.ended) state.body.awakeHours = Math.max(0, (minutes - 390) / 60 * 0.18);
    if (dayNumber() > startDay && !state.ended) {
      state.world.marketStock = state.world.marketStock || {};
      state.body.condition = Math.min(100, state.body.condition + (wasSleeping ? 2 : 0));
    }
  }

  function endGame(title, text, success = false) {
    state.ended = { title, text, success };
    addLog(title + '.', success ? 'important' : 'danger');
  }

  function perform(minutes, options, message, effect) {
    advanceTime(minutes, options || {});
    if (!state.ended && typeof effect === 'function') effect();
    if (message && !state.ended) addLog(message, options?.logType || '');
    saveState();
    render();
  }

  function itemCount(key) { return Math.max(0, Number(state.inventory[key] || 0)); }
  function addItem(key, amount = 1) { state.inventory[key] = itemCount(key) + amount; }
  function takeItem(key, amount = 1) {
    if (itemCount(key) < amount) return false;
    state.inventory[key] -= amount;
    return true;
  }

  function workAtMarket() {
    const day = dayNumber();
    const tier = marketLevel(day);
    const workedDays = state.world.workedDays || (state.world.workedDays = []);
    if (state.current !== 'market' || tier.key === 'closed' || workedDays.includes(day) || state.people.yann.location !== 'market') {
      notify('Il n’y a pas de travail disponible ici maintenant.');
      return;
    }
    const wage = day <= 2 ? 14 : day <= 5 ? 10 : 5;
    perform(75, { riskLocation: 'market', logType: 'important' }, 'Vous aidez Yann à trier les livraisons et à ranger les produits derrière le comptoir.', () => {
      state.world.workedDays.push(day);
      state.money += wage;
      state.people.yann.trust = Math.min(5, state.people.yann.trust + 1);
      state.people.yann.trustDay = day;
      addLog(`Yann vous paie ${moneyText(wage)}. Le travail se fait plus rare à mesure que les livraisons cessent.`, 'important');
    });
  }

  function barter(itemGiven, itemReceived) {
    if (state.current !== 'townhall' || dayNumber() < 7 || itemCount(itemGiven) <= itemCount(itemReceived)) {
      notify('Personne ne propose cet échange pour le moment.');
      return;
    }
    const labels = { water: 'une bouteille d’eau', ration: 'un repas' };
    perform(10, { riskLocation: 'townhall' }, `Au point de rassemblement, vous troquez ${labels[itemGiven]} contre ${labels[itemReceived]}.`, () => {
      takeItem(itemGiven);
      addItem(itemReceived);
    });
  }

  function searchLocation() {
    const location = state.current;
    const minutes = location === 'home' ? 18 : 35;
    const loot = {
      home: ['water', 'soap', 'ration', 'nothing'],
      market: ['ration', 'water', 'soap', 'nothing', 'nothing'],
      clinic: ['medkit', 'soap', 'nothing', 'nothing'],
      townhall: ['water', 'ration', 'nothing', 'nothing'],
      depot: ['water', 'ration', 'mask', 'nothing', 'nothing'],
      square: ['nothing', 'water', 'nothing', 'nothing'],
    }[location] || ['nothing'];
    const found = loot[Math.floor(Math.random() * loot.length)];
    const description = found === 'nothing' ? 'Vous ne trouvez rien d’utile, seulement des traces de passage.' : `Vous trouvez : ${ITEMS[found].label.toLowerCase()}.`;
    perform(minutes, { riskLocation: location }, `Fouille : ${description}`, () => {
      if (found !== 'nothing') addItem(found, 1);
      if (location === 'market' && Math.random() < 0.12 && state.money < 80) {
        state.money += 3;
        addLog('Quelques pièces oubliées sous le comptoir : 3 €.', '');
      }
    });
  }

  function talkTo(id, share = false) {
    const person = PEOPLE.find(p => p.id === id);
    const data = state.people[id];
    if (!person || !data || data.location !== state.current || !data.safe) return;
    if (share && !takeItem('ration')) { notify('Vous n’avez pas de repas à partager.'); return; }
    const firstMeeting = data.met === undefined ? data.trust === 0 : !data.met;
    const lines = {
      lila: firstMeeting ? 'Lila vous reconnaît. Elle demande si vous avez vu sa sœur; personne ne répond à ses appels depuis l’aube.' : 'Lila a entendu parler d’un rassemblement à la mairie. Elle vous conseille de ne pas vous fier aux rumeurs non confirmées.',
      yann: firstMeeting ? 'Yann balaie la file du regard. « Je ne sais pas combien de jours on pourra tenir comme ça. Prenez seulement ce dont vous avez besoin. »' : 'Yann vous glisse que les livraisons ne viendront probablement plus. Il garde quelques produits derrière le comptoir.',
      mina: firstMeeting ? 'Mina parle vite, mais reste calme. Elle demande aux habitants de garder leurs distances et de signaler les symptômes sans se rendre directement au dispensaire.' : 'Mina est épuisée. Elle vous rappelle que les informations changent d’une heure à l’autre et qu’il faut éviter les attroupements.',
    };
    const message = share ? `Vous partagez un repas avec ${person.name.split(' ')[0]}.` : lines[id];
    const day = dayNumber();
    perform(share ? 18 : 13, { riskLocation: state.current }, message, () => {
      if (data.trustDay !== day) {
        data.trust = Math.min(5, data.trust + (share ? 2 : 1));
        data.trustDay = day;
      }
      data.met = true;
      data.memory = [...(data.memory || []), share ? 'repas partagé' : 'conversation'].slice(-6);
      if (share && id === 'lila') addLog('Lila vous remercie et promet de garder un œil sur votre appartement.', 'important');
      if (id === 'mina' && state.infection && state.infection.symptomatic) {
        state.body.condition = Math.min(100, state.body.condition + 4);
        state.infection.severity = Math.max(0, state.infection.severity - 4);
        addLog('Mina vous fait asseoir et vous conseille de vous reposer et de boire.', '');
      }
    });
  }

  function requestFavor(id) {
    const person = PEOPLE.find(p => p.id === id);
    const data = state.people[id];
    const day = dayNumber();
    if (!person || !data || data.location !== state.current || !data.safe || data.sick || data.trust < 2 || data.favorDay === day) {
      notify('Cette personne ne peut pas vous aider pour le moment.');
      return;
    }
    if (id === 'yann' && marketLevel(day).key === 'closed') { notify('La boutique de Yann est fermée.'); return; }
    const effect = () => {
      data.favorDay = day;
      data.memory = [...(data.memory || []), 'aide apportée'].slice(-6);
      if (id === 'mina') {
        state.body.condition = Math.min(100, state.body.condition + 8);
        if (state.infection) state.infection.severity = Math.max(0, state.infection.severity - 8);
        addLog('Mina prend quelques minutes pour vous examiner. Elle a peu de matériel, mais se souvient de votre confiance.', 'important');
      } else if (id === 'yann') {
        const options = ['water', 'ration', 'soap'].filter(key => (state.world.marketStock[key] || 0) > 0 && itemCount(key) < (key === 'soap' ? 1 : 2));
        if (options.length) {
          const key = options[0];
          state.world.marketStock[key] -= 1;
          addItem(key);
          addLog(`Yann vous met de côté ${ITEMS[key].label.toLowerCase()}, sans vous le faire payer.`, 'important');
        } else {
          state.body.condition = Math.min(100, state.body.condition + 3);
          addLog('Yann n’a plus rien à donner, mais vous laisse souffler quelques minutes à l’abri.', 'important');
        }
      } else {
        let key = itemCount('water') < 2 ? 'water' : itemCount('ration') < 2 ? 'ration' : itemCount('soap') < 1 ? 'soap' : null;
        if (key) {
          addItem(key);
          addLog(`Lila vous donne ${ITEMS[key].label.toLowerCase()} qu’elle avait mis de côté pour le voisinage.`, 'important');
        } else {
          state.body.condition = Math.min(100, state.body.condition + 3);
          addLog('Lila veille sur l’immeuble pendant que vous reprenez votre souffle.', 'important');
        }
      }
    };
    perform(15, { riskLocation: state.current }, `${person.name.split(' ')[0]} accepte de vous donner un coup de main.`, effect);
  }

  function useItem(kind) {
    if (kind === 'drink') {
      if (!takeItem('water')) { notify('Il ne vous reste pas d’eau.'); return; }
      perform(4, { riskLocation: state.current }, 'Vous buvez lentement. La gorge cesse de vous brûler.', () => { state.body.lastDrink = state.absMin; });
    } else if (kind === 'eat') {
      if (!takeItem('ration')) { notify('Vous n’avez plus de repas emballé.'); return; }
      perform(12, { riskLocation: state.current }, 'Vous mangez un repas froid. Ce n’est pas grand-chose, mais ça aide.', () => { state.body.lastEat = state.absMin; });
    } else if (kind === 'toilet') {
      perform(10, { riskLocation: state.current }, 'Vous trouvez un moment d’intimité et soulagez vos besoins naturels.', () => { state.body.lastToilet = state.absMin; state.body.lastBowel = state.absMin; });
    } else if (kind === 'wash') {
      if (!takeItem('soap')) { notify('Vous n’avez plus de savon.'); return; }
      if (!state.world.waterService && !takeItem('water')) { addItem('soap', 1); notify('Sans eau courante, il vous faut une bouteille d’eau pour vous laver.'); return; }
      perform(22, { riskLocation: state.current }, 'Vous vous lavez comme vous pouvez. Un petit répit dans une journée déjà trop longue.', () => { state.body.lastWash = state.absMin; });
    } else if (kind === 'sleep') {
      perform(8 * 60, { riskLocation: state.current, sleeping: true }, 'Vous dormez quelques heures. Au réveil, la lumière a changé et la radio ne parle plus tout à fait de la même ville.', () => {});
    } else if (kind === 'radio') {
      perform(18, { riskLocation: state.current }, 'Vous écoutez le bulletin jusqu’au bout, malgré les grésillements.', () => {
        const phase = phaseForDay();
        addLog(`La radio parle de « ${phase.label.toLowerCase()} ». Aucun chiffre fiable n’est communiqué.`, 'important');
      });
    } else if (kind === 'mask') {
      if (!takeItem('mask')) { notify('Vous n’avez plus de masque.'); return; }
      perform(2, { riskLocation: state.current }, 'Vous ajustez un masque filtrant. Il ne protège pas de tout, mais limite les expositions.', () => { state.maskUntil = state.absMin + 3 * 60; });
    } else if (kind === 'care') {
      if (state.current !== 'clinic' || dayNumber() >= 13) return;
      const price = dayNumber() >= 8 ? 0 : 6;
      if (state.money < price) { notify('Vous n’avez pas assez d’argent pour les soins.'); return; }
      state.money -= price;
      perform(35, { riskLocation: 'clinic' }, price ? 'Mina vérifie vos symptômes et vous indique quoi surveiller.' : 'Mina vous installe dans un coin calme, loin de la file.', () => {
        state.body.condition = Math.min(100, state.body.condition + 9);
        if (state.infection) state.infection.severity = Math.max(0, state.infection.severity - 11);
      });
    }
  }

  function buyItem(key) {
    const tier = marketLevel();
    const stock = state.world.marketStock[key] || 0;
    const price = marketPrice(key);
    if (state.current !== 'market' || tier.key === 'closed' || stock <= 0) { notify('Ce produit n’est plus disponible.'); return; }
    if (state.money < price) { notify('Vous n’avez pas assez d’argent.'); return; }
    state.money -= price;
    state.world.marketStock[key] -= 1;
    perform(6, { riskLocation: 'market' }, `Vous achetez ${ITEMS[key].label.toLowerCase()} pour ${moneyText(price)}.`, () => addItem(key, 1));
  }

  function searchForEndCondition() {
    const day = dayNumber();
    if (state.current === 'depot' && day >= 18) {
      const infected = state.infection && state.infection.symptomatic;
      if (infected) {
        endGame('Le convoi ne vous prend pas', 'La fièvre est visible. Les responsables du convoi vous demandent de rester en retrait; les moteurs s’éloignent dans la brume.');
      } else if (!itemCount('water') || !itemCount('ration')) {
        notify('Pour partir, il vous faut au moins une bouteille d’eau et un repas.');
        return;
      } else {
        takeItem('water');
        takeItem('ration');
        endGame('Vous quittez Penmarch', 'Le car démarre à l’aube. À travers la vitre, la ville disparaît derrière un rideau de pluie. Vous ignorez ce qui vous attend, mais vous êtes vivant.', true);
      }
      saveState(); render();
    }
  }

  function travel() {
    const target = state.selected;
    if (!target || target === state.current || !LOCATIONS[target] || state.ended) return;
    const duration = travelMinutes(state.current, target);
    const riskPlace = target;
    perform(duration, { riskLocation: riskPlace, isTravel: true }, `Vous rejoignez ${LOCATIONS[target].short.toLowerCase()}.`, () => {
      state.current = target;
      state.selected = null;
    });
    if (!state.ended) {
      searchForEndCondition();
      saveState();
      render();
    }
  }

  function actionData() {
    const result = [];
    const add = (key, label, icon, cost, disabled = false) => result.push({ key, label, icon, cost, disabled });
    if (itemCount('water') > 0) add('drink', 'Boire un peu d’eau', '◒', '4 min');
    if (itemCount('ration') > 0) add('eat', 'Manger un repas', '◇', '12 min');
    if (itemCount('mask') > 0 && state.maskUntil <= state.absMin) add('mask', 'Mettre un masque', '▱', '2 min');
    const facilities = ['home', 'clinic', 'townhall'].includes(state.current);
    if (facilities) add('toilet', 'Aller aux toilettes', '⌁', '10 min');
    if (state.current === 'home' && itemCount('soap') > 0) {
      const canWash = state.world.waterService || itemCount('water') > 0;
      add('wash', 'Se laver', '✳', canWash ? '22 min' : 'Eau manquante', !canWash);
      add('sleep', 'Dormir quelques heures', '☾', '8 h');
      add('radio', 'Écouter la radio', '⌁', '18 min');
    } else if (state.current === 'home') {
      add('sleep', 'Dormir quelques heures', '☾', '8 h');
      add('radio', 'Écouter la radio', '⌁', '18 min');
    }
    if (state.current === 'market') {
      const tier = marketLevel();
      const workedDays = state.world.workedDays || [];
      if (tier.key !== 'closed' && !workedDays.includes(dayNumber()) && state.people.yann.location === 'market') {
        add('work', 'Aider Yann à la boutique', '⚒', `1 h 15 · ${moneyText(dayNumber() <= 2 ? 14 : dayNumber() <= 5 ? 10 : 5)}`);
      }
      for (const key of ['water', 'ration', 'mask', 'soap', 'medkit']) {
        const stock = state.world.marketStock[key] || 0;
        const price = marketPrice(key);
        const closed = tier.key === 'closed' || stock <= 0 || state.money < price;
        const suffix = stock <= 0 ? 'Rupture' : tier.key === 'closed' ? 'Fermé' : moneyText(price);
        add(`buy:${key}`, `Acheter · ${ITEMS[key].short}`, ITEMS[key].icon, suffix, closed);
      }
    }
    if (state.current === 'clinic' && dayNumber() < 13) {
      const price = dayNumber() >= 8 ? 'Gratuit' : '6 €';
      add('care', 'Demander des soins', '✚', `35 min · ${price}`, dayNumber() < 8 && state.money < 6);
    }
    if (state.current === 'townhall' && dayNumber() >= 7) {
      if (itemCount('ration') > itemCount('water')) add('trade:water', 'Troquer un repas contre de l’eau', '◈', '10 min');
      else if (itemCount('water') > itemCount('ration')) add('trade:ration', 'Troquer de l’eau contre un repas', '◈', '10 min');
    }
    add('search', 'Fouiller les alentours', '⌕', state.current === 'home' ? '18 min' : '35 min');
    for (const p of PEOPLE) {
      const person = state.people[p.id];
      if (person.location === state.current && person.safe) {
        add(`talk:${p.id}`, `Parler à ${p.name.split(' ')[0]}`, '◌', '13 min');
        if (itemCount('ration') > 0 && (p.id === 'lila' || person.trust >= 1)) add(`share:${p.id}`, `Partager un repas avec ${p.name.split(' ')[0]}`, '◇', '18 min');
        if (person.trust >= 2 && !person.sick && person.favorDay !== dayNumber()) add(`favor:${p.id}`, `Demander un coup de main à ${p.name.split(' ')[0]}`, '✳', '15 min');
      }
    }
    if (state.current === 'depot' && dayNumber() >= 18) add('escape', 'Monter dans le convoi', '▣', 'Une chance de partir', false);
    return result;
  }

  function handleAction(key) {
    if (state.ended) return;
    if (key.startsWith('buy:')) return buyItem(key.split(':')[1]);
    if (key.startsWith('talk:')) return talkTo(key.split(':')[1]);
    if (key.startsWith('share:')) return talkTo(key.split(':')[1], true);
    if (key.startsWith('favor:')) return requestFavor(key.split(':')[1]);
    if (key.startsWith('trade:')) return barter(key.split(':')[1] === 'water' ? 'ration' : 'water', key.split(':')[1]);
    if (key === 'work') return workAtMarket();
    if (key === 'search') return searchLocation();
    if (key === 'escape') return searchForEndCondition();
    return useItem(key);
  }

  function needClass(tier) {
    if (tier >= 3) return 'urgent';
    if (tier >= 2) return 'notice';
    return '';
  }

  function generalConditionText() {
    if (state.infection?.symptomatic) {
      if (state.infection.strain === 'late') return 'Fièvre forte · comportement inhabituel';
      if (state.infection.severity > 45) return 'Fièvre persistante · très affaibli';
      return 'Fièvre et douleurs · contagion possible';
    }
    if (state.infection) return 'Vous surveillez l’apparition de symptômes';
    if (state.body.condition < 30) return 'État critique · vous devez vous mettre à l’abri';
    if (state.body.condition < 60) return 'État fragile · ralentissez le rythme';
    const urgent = needs().some(n => n.tier >= 3);
    return urgent ? 'Fatigue et inconfort s’accumulent' : 'État général : stable';
  }

  function renderNeeds() {
    const list = document.getElementById('needs-list');
    list.innerHTML = needs().map(n => `<li class="need-item ${needClass(n.tier)}"><span class="need-icon" aria-hidden="true">${n.icon}</span><span><strong>${n.title} :</strong> ${n.text}</span></li>`).join('');
    document.getElementById('general-condition').textContent = generalConditionText();
    const dot = document.querySelector('.condition-dot');
    dot.className = `condition-dot${state.body.condition < 30 ? ' danger' : state.body.condition < 60 || needs().some(n => n.tier >= 3) ? ' attention' : ''}`;
  }

  function renderMap() {
    const holder = document.getElementById('map-locations');
    holder.innerHTML = Object.entries(LOCATIONS).map(([key, loc]) => {
      const isCurrent = key === state.current;
      const isSelected = key === state.selected;
      const time = isCurrent ? 'Vous êtes ici' : `${travelMinutes(state.current, key)} min à pied`;
      return `<button type="button" class="location-option${isCurrent ? ' current' : ''}${isSelected ? ' selected' : ''}" data-location="${key}" ${isCurrent || state.ended ? 'disabled' : ''} aria-pressed="${isSelected}">
        <span class="loc-topline"><span class="loc-icon" aria-hidden="true">${loc.icon}</span>${loc.short}</span>
        <span class="loc-meta">${isCurrent ? 'Votre position' : time} · ${locationAvailability(key)}</span>
      </button>`;
    }).join('');
    const chosen = state.selected ? LOCATIONS[state.selected] : null;
    const hint = document.getElementById('travel-hint');
    const button = document.getElementById('travel-button');
    if (chosen) {
      const mins = travelMinutes(state.current, state.selected);
      hint.textContent = `À pied vers ${chosen.short.toLowerCase()} · environ ${mins} minutes. L’exposition dépend du trajet et de la crise.`;
      button.textContent = `Partir · ${mins} min`;
      button.disabled = Boolean(state.ended);
    } else {
      hint.textContent = state.ended ? 'Cette partie est terminée.' : 'Choisissez une destination; le trajet fera avancer l’heure.';
      button.textContent = state.current === 'home' ? 'Vous êtes chez vous' : 'Choisir une destination';
      button.disabled = true;
    }
  }

  function renderActions() {
    const holder = document.getElementById('action-list');
    const actions = actionData();
    holder.innerHTML = actions.map(a => `<button type="button" class="action-button" data-action="${a.key}" ${a.disabled || state.ended ? 'disabled' : ''}>
      <span class="action-main"><span class="action-icon" aria-hidden="true">${a.icon}</span><span class="action-label">${a.label}</span></span><span class="action-cost">${a.cost}</span>
    </button>`).join('');
  }

  function currentGoal(id) {
    const p = PEOPLE.find(person => person.id === id);
    const d = state.people[id];
    if (!d.safe) return 'introuvable';
    return d.goal || ({ lila: 'prendre des nouvelles du quartier', yann: 'garder la boutique ouverte', mina: 'maintenir le dispensaire' })[id];
  }

  function whereabouts(id) {
    const data = state.people[id];
    if (!data.safe) return 'Silence depuis plusieurs heures';
    const location = LOCATIONS[data.location];
    const status = data.sick ? 'Semble malade' : data.trust >= 3 ? 'Vous fait confiance' : data.trust >= 2 ? 'Peut vous aider' : data.trust >= 1 ? 'Vous connaît' : 'A ses propres priorités';
    return `${location ? location.short : 'Inconnu'} · ${status}`;
  }

  function renderPeople() {
    const people = document.getElementById('people-list');
    people.innerHTML = PEOPLE.map(p => {
      const data = state.people[p.id];
      return `<div class="person-row"><span class="person-avatar" aria-hidden="true">${p.initial}</span><span><span class="person-name">${p.name}</span><br><span class="person-role">${p.role}</span></span><span class="person-goal">${currentGoal(p.id)}<small>${whereabouts(p.id)}</small></span></div>`;
    }).join('');
    const present = PEOPLE.filter(p => state.people[p.id].location === state.current && state.people[p.id].safe);
    document.getElementById('scene-people').innerHTML = present.length
      ? present.map(p => `<span class="person-chip">${p.name.split(' ')[0]} est là</span>`).join('')
      : '<span class="person-chip empty">Personne à proximité</span>';
  }

  function renderInventory() {
    const holder = document.getElementById('inventory-list');
    const stocked = Object.entries(state.inventory).filter(([, count]) => count > 0);
    holder.innerHTML = stocked.length
      ? stocked.map(([key, count]) => `<span class="inventory-item">${ITEMS[key].short}<b>×${count}</b></span>`).join('')
      : '<span class="inventory-empty">Vos poches sont vides.</span>';
    document.getElementById('money-amount').textContent = moneyText(state.money);
  }

  function renderWorld() {
    const day = dayNumber();
    const phase = phaseForDay(day);
    document.getElementById('date-label').textContent = `JOUR ${String(day).padStart(2, '0')} · ${DAY_NAMES[(day - 1) % DAY_NAMES.length]}`;
    document.getElementById('clock').textContent = clockText();
    document.getElementById('note-date').textContent = clockText();
    document.getElementById('outbreak-phase').textContent = phase.label;
    document.getElementById('outbreak-copy').textContent = phase.copy;
    const indicator = document.getElementById('outbreak-indicator');
    indicator.textContent = phase.indicator;
    if (phase.key === 'reanimation') indicator.style.color = 'var(--danger)';
    else if (phase.key === 'mutation') indicator.style.color = 'var(--warn)';
    else indicator.style.color = '';
    document.getElementById('services-status').textContent = !state.world.power ? 'Coupures de courant' : day >= 8 ? 'Services réduits' : 'Services actifs';
    document.getElementById('broadcast-status').textContent = day >= 16 ? 'RADIO LOCALE · SILENCE' : day >= 8 ? 'RADIO LOCALE · INTERMITTENTE' : 'RADIO LOCALE · FAIBLE';
    document.getElementById('daily-note').textContent = day < 3
      ? 'Les volets s’ouvrent un à un dans la rue. Quelque part, une sirène s’arrête.'
      : day < 7 ? 'La file devant l’épicerie s’allonge. Les gens parlent moins fort qu’hier.'
      : day < 12 ? 'Les rideaux restent fermés. On entend des pas pressés dans la cage d’escalier.'
      : day < 16 ? 'La radio saute d’une fréquence à l’autre. La ville semble retenir son souffle.'
      : 'Il fait nuit même en plein jour. Les bruits derrière les portes ne ressemblent plus à des voix.';
    document.getElementById('location-title').textContent = LOCATIONS[state.current].name;
    const loc = LOCATIONS[state.current];
    let description = loc.scene;
    if (state.current === 'market') {
      const market = marketLevel();
      description = market.key === 'closed' ? 'Le rideau métallique est baissé. Derrière la vitre, quelques rayons vides et des affiches arrachées.' : market.key === 'rationed' ? 'Une file s’étire sous la pluie. Le commerçant laisse entrer les habitants un par un.' : market.key === 'limited' ? 'Le rideau est levé, mais les rayons ont été éclaircis. Yann surveille la rue.' : loc.scene;
    }
    if (state.current === 'clinic' && day >= 8) description = 'Le dispensaire reçoit encore quelques personnes, mais les consultations ordinaires ont cessé. Mina fait de son mieux avec ce qui reste.';
    if (!state.world.power && state.current === 'home') description = 'L’appartement est plongé dans une lumière grise. La radio fonctionne encore sur piles; le réfrigérateur s’est tu.';
    document.getElementById('scene-description').textContent = description;
    document.getElementById('weather-tag').textContent = day >= 16 ? 'Nuit · pluie froide' : day >= 8 ? 'Averses · 9°' : 'Bruine fine · 12°';
    document.getElementById('money-amount').textContent = moneyText(state.money);
  }

  function renderLog() {
    const holder = document.getElementById('event-log');
    holder.innerHTML = state.log.slice(0, 9).map(item => `<li class="log-entry ${item.type || ''}"><span class="log-time">${item.time}</span><span>${item.text}</span></li>`).join('');
  }

  function renderEnding() {
    const panel = document.getElementById('ending-panel');
    if (!state.ended) { panel.classList.add('hidden'); panel.innerHTML = ''; return; }
    panel.classList.remove('hidden');
    panel.innerHTML = `<h2>${state.ended.title}</h2><p>${state.ended.text}</p><button class="button button-primary" id="ending-reset" type="button" style="margin-top:12px">Recommencer</button>`;
    document.getElementById('ending-reset').addEventListener('click', resetGame);
  }

  function render() {
    renderWorld();
    renderNeeds();
    renderMap();
    renderActions();
    renderPeople();
    renderInventory();
    renderLog();
    renderEnding();
  }

  function resetGame() {
    if (!window.confirm('Recommencer une nouvelle partie ? La sauvegarde actuelle sera remplacée.')) return;
    state = freshState();
    saveState();
    render();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    notify('Une nouvelle journée commence.');
  }

  document.getElementById('map-locations').addEventListener('click', (event) => {
    const button = event.target.closest('[data-location]');
    if (!button || button.disabled) return;
    state.selected = button.dataset.location;
    renderMap();
  });
  document.getElementById('travel-button').addEventListener('click', travel);
  document.getElementById('action-list').addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button || button.disabled) return;
    handleAction(button.dataset.action);
  });
  document.getElementById('reset-button').addEventListener('click', resetGame);

  // Annonce l'objectif de fin sans imposer un chemin unique; le joueur peut survivre autrement.
  render();
  saveState();
})();
