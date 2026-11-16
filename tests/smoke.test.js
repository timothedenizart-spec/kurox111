const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'src', 'game.js'), 'utf8');

class MockElement {
  constructor() {
    this.textContent = '';
    this.innerHTML = '';
    this.disabled = false;
    this.dataset = {};
    this.style = {};
    this.listeners = {};
    this.classes = new Set();
    this.classList = {
      add: (name) => this.classes.add(name),
      remove: (name) => this.classes.delete(name),
    };
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
}

function bootGame(seed = null) {
  const elements = new Map();
  const getElement = (id) => {
    if (!elements.has(id)) elements.set(id, new MockElement());
    return elements.get(id);
  };
  const storage = new Map(seed ? [['veille-save-v1', JSON.stringify(seed)]] : []);
  const deterministicMath = Object.create(Math);
  deterministicMath.random = () => 0.99;
  const document = { getElementById: getElement, querySelector: () => new MockElement() };
  const sandbox = {
    document,
    window: { confirm: () => true, scrollTo: () => {} },
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
    },
    Math: deterministicMath,
    setTimeout: () => 1,
    clearTimeout: () => {},
  };
  vm.runInNewContext(source, sandbox);
  return { get: getElement, storage };
}

function clickAction(game, action) {
  game.get('action-list').listeners.click({
    target: { closest: () => ({ dataset: { action }, disabled: false }) },
  });
}

function lateGameSeed({ current = 'depot', infection = null } = {}) {
  const absMin = 17 * 1440 + 8 * 60;
  return {
    version: 1,
    absMin,
    current,
    selected: null,
    money: 20,
    inventory: { water: 1, ration: 1, mask: 0, soap: 0, medkit: 0 },
    body: {
      lastDrink: absMin - 60, lastEat: absMin - 3 * 60, awakeHours: 1,
      lastToilet: absMin - 60, lastBowel: absMin - 5 * 60,
      lastWash: absMin - 10 * 60, condition: 95,
    },
    maskUntil: 0,
    infection,
    world: {
      processedDay: 18, activeCases: 2000, cumulativeCases: 4000, deaths: 100,
      marketStock: { water: 0, ration: 0, mask: 0, soap: 0, medkit: 0 },
      clinicOpen: false, power: false, waterService: false, convoyAnnounced: true,
      outbreakName: 'La fièvre de Penmarch',
    },
    people: {
      lila: { location: 'home', trust: 0, infectionAt: null, sick: false, safe: true, goal: 'aider' },
      yann: { location: 'home', trust: 0, infectionAt: null, sick: false, safe: true, goal: 'protéger' },
      mina: { location: 'home', trust: 0, infectionAt: null, sick: false, safe: true, goal: 'soigner' },
    },
    log: [],
    ended: null,
  };
}

test('démarre, avance l’horloge, permet un déplacement et sauvegarde', () => {
  const game = bootGame();
  assert.equal(game.get('clock').textContent, '07:20');
  assert.match(game.get('action-list').innerHTML, /Boire un peu d’eau/);

  clickAction(game, 'drink');
  assert.equal(game.get('clock').textContent, '07:24');

  game.get('map-locations').listeners.click({
    target: { closest: () => ({ dataset: { location: 'market' }, disabled: false }) },
  });
  assert.match(game.get('travel-button').textContent, /18 min/);
  game.get('travel-button').listeners.click();
  assert.equal(game.get('clock').textContent, '07:42');
  assert.match(game.get('location-title').textContent, /Épicerie/);
  assert.ok(game.storage.get('veille-save-v1'));
});

test('le travail au début de la crise procure des espèces une fois par jour', () => {
  const game = bootGame();
  game.get('map-locations').listeners.click({
    target: { closest: () => ({ dataset: { location: 'market' }, disabled: false }) },
  });
  game.get('travel-button').listeners.click();
  assert.match(game.get('action-list').innerHTML, /Aider Yann à la boutique/);
  clickAction(game, 'work');
  assert.equal(game.get('clock').textContent, '08:53');
  assert.equal(game.get('money-amount').textContent, '52 €');
  assert.doesNotMatch(game.get('action-list').innerHTML, /Aider Yann à la boutique/);
});

test('le troc remplace les espèces lorsque les commerces se replient', () => {
  const seed = lateGameSeed({ current: 'townhall' });
  seed.inventory.ration = 2;
  seed.inventory.water = 0;
  const game = bootGame(seed);
  assert.match(game.get('action-list').innerHTML, /Troquer un repas contre de l’eau/);
  clickAction(game, 'trade:water');
  assert.equal(game.get('clock').textContent, '08:10');
  assert.match(game.get('inventory-list').innerHTML, /Eau/);
  assert.doesNotMatch(game.get('action-list').innerHTML, /Troquer un repas contre de l’eau/);
});

test('un lien de confiance permet de demander une aide mémorisée à un PNJ', () => {
  const seed = lateGameSeed({ current: 'townhall' });
  seed.people.lila.location = 'townhall';
  seed.people.lila.trust = 2;
  seed.people.lila.trustDay = 17;
  seed.people.lila.favorDay = 17;
  seed.inventory.water = 0;
  seed.inventory.ration = 1;
  const game = bootGame(seed);
  assert.match(game.get('action-list').innerHTML, /Demander un coup de main à Lila/);
  clickAction(game, 'favor:lila');
  assert.equal(game.get('clock').textContent, '08:15');
  assert.match(game.get('inventory-list').innerHTML, /Eau/);
  assert.doesNotMatch(game.get('action-list').innerHTML, /Demander un coup de main à Lila/);
});

test('un PNJ malade s’isole au lieu de suivre sa routine habituelle', () => {
  const seed = lateGameSeed({ current: 'home' });
  seed.absMin = 7 * 60 + 50;
  seed.world.processedDay = 1;
  seed.people.lila.location = 'square';
  seed.people.lila.infectionAt = seed.absMin - 50 * 60;
  seed.people.lila.sick = false;
  const game = bootGame(seed);
  clickAction(game, 'sleep');
  assert.match(game.get('people-list').innerHTML, /Chez vous · Semble malade/);
  assert.match(game.get('people-list').innerHTML, /s’isoler et protéger ses proches/);
});

test('le convoi permet une fin de survie si les provisions sont réunies', () => {
  const game = bootGame(lateGameSeed());
  assert.match(game.get('action-list').innerHTML, /Monter dans le convoi/);
  clickAction(game, 'escape');
  assert.match(game.get('ending-panel').innerHTML, /Vous quittez Penmarch/);
});

test('une infection tardive peut aboutir à une fin tragique', () => {
  const absMin = 15 * 1440 + 8 * 60;
  const seed = lateGameSeed({
    current: 'home',
    infection: { exposedAt: absMin - 200 * 60, symptomatic: true, severity: 99, strain: 'late' },
  });
  seed.absMin = absMin;
  seed.world.processedDay = 16;
  const game = bootGame(seed);
  clickAction(game, 'sleep');
  assert.match(game.get('ending-panel').innerHTML, /Vous n’êtes plus vous-même/);
});
