import { LOCATIONS, PandemicSimulation } from "./simulation.js";

const game = new PandemicSimulation();

const element = (id) => document.getElementById(id);
const labels = {
  water: "Eau potable",
  food: "Nourriture",
  soap: "Savon",
  medicine: "Médicaments",
};

const notice = element("action-notice");

function actionButton(action, title, detail, disabled = false, extra = "") {
  return `<button class="action-button" type="button" data-action="${action}" ${extra} ${disabled ? "disabled" : ""}>${title}<span>${detail}</span></button>`;
}

function renderInventory(player) {
  element("money-display").textContent = `${player.money} crédits`;
  element("inventory-list").innerHTML = Object.entries(player.inventory)
    .map(([item, amount]) => `<li><span>${labels[item]}</span><strong>${amount}</strong></li>`)
    .join("");
}

function renderNeeds(needs) {
  const active = needs.filter((need) => need.severity !== "calm");
  element("needs-list").innerHTML = active.length
    ? active
      .map(
        (need) => `<article class="need-signal ${need.severity}"><strong>${need.label}</strong><p>${need.message}</p></article>`,
      )
      .join("")
    : '<p class="calm-copy">Rien de pressant. Garde tout de même un œil sur l’heure.</p>';
}

function renderLocation(snapshot) {
  element("location-title").textContent = snapshot.location.name;
  element("location-description").textContent = snapshot.location.description;
  element("nearby-residents").innerHTML = snapshot.nearby.length
    ? snapshot.nearby
      .map(
        (resident) => `<span class="resident-chip"><strong>${resident.name}</strong> · ${resident.state}, ${resident.intent} · ${resident.relation}</span>`,
      )
      .join("")
    : '<span class="empty-residents">Personne ne s’attarde près de toi.</span>';
}

function renderActions(snapshot) {
  const { player, location, marketOpen, prices, phase } = snapshot;
  const canWash = ["apartment", "clinic"].includes(player.location) && (player.location !== "apartment" || player.inventory.soap > 0);
  const canToilet = ["apartment", "clinic", "hall"].includes(player.location);

  const sleepDetail = location.id === "apartment"
    ? player.shelterSecured || phase.index < 3
      ? "7 h · sommeil plus sûr"
      : "5 h · porte non préparée"
    : location.id === "hall" && player.refugeAccess
      ? "6 h · repos partagé"
      : "3 h · repos incertain";

  element("care-actions").innerHTML = [
    actionButton("drink", "Boire", "10 min · utilise 1 eau", player.inventory.water < 1),
    actionButton("eat", "Manger", "20 min · utilise 1 nourriture", player.inventory.food < 1),
    actionButton("sleep", "Se reposer", sleepDetail),
    actionButton("wash", "Te laver", "20 min · discrétion requise", !canWash),
    actionButton("toilet", "Trouver des toilettes", "8 min · lieu adapté requis", !canToilet),
  ].join("");

  const talkDisabled = snapshot.nearby.length === 0;
  const workDisabled = location.id !== "workshop" || !phase.workAvailable;
  const buyWaterDisabled = location.id !== "market" || !marketOpen || !prices.water || player.money < prices.water;
  const buyFoodDisabled = location.id !== "market" || !marketOpen || !prices.food || player.money < prices.food;
  const shareWaterDisabled = talkDisabled || player.inventory.water < 1;
  const shareFoodDisabled = talkDisabled || player.inventory.food < 1;
  const knownNeighbor = snapshot.nearby.some((resident) => ["te reconnaît", "te fait confiance"].includes(resident.relation));
  const aidDisabled = !knownNeighbor || player.favours < 1 || phase.index < 2;

  element("world-actions").innerHTML = [
    actionButton("talk", "Parler", "25 min · créer un premier lien", talkDisabled),
    actionButton("share", "Offrir de l’eau", "15 min · une aide qui compte", shareWaterDisabled, 'data-item="water"'),
    actionButton("share", "Offrir de la nourriture", "15 min · bâtir la confiance", shareFoodDisabled, 'data-item="food"'),
    actionButton("aid", "Demander une faveur", phase.index >= 2 ? "15 min · le réseau plutôt que l’argent" : "le réseau comptera après la rupture", aidDisabled),
    actionButton("work", "Travailler", phase.workAvailable ? "4 h · crédits contre du temps" : "l’atelier ne paie plus", workDisabled),
    actionButton("buy", prices.water ? `Acheter de l’eau · ${prices.water} cr.` : "L’eau ne s’achète plus", "12 min · marché ouvert", buyWaterDisabled, 'data-item="water"'),
    actionButton("buy", prices.food ? `Acheter de la nourriture · ${prices.food} cr.` : "La nourriture ne s’achète plus", "12 min · marché ouvert", buyFoodDisabled, 'data-item="food"'),
  ].join("");
}

function renderTravel(currentLocation) {
  element("location-list").innerHTML = LOCATIONS.map(
    (location) => `<button class="place-button ${location.id === currentLocation ? "is-current" : ""}" type="button" data-action="move" data-location="${location.id}" ${location.id === currentLocation ? "disabled" : ""}>${location.name}<small>${location.description}</small></button>`,
  ).join("");
}

function renderWorld(snapshot) {
  const { phase, world } = snapshot;
  element("phase-title").textContent = phase.title;
  element("phase-summary").textContent = phase.summary;
  const affected = world.population.exposed + world.population.ill;
  const altered = world.population.altered;
  element("world-facts").innerHTML = [
    ["Marché Cédre", `Le marché est ${world.market}.`],
    ["Dispensaire", world.clinic],
    ["Échanges", world.currency],
    ["Réseau", world.network],
    ["Abri", world.shelter],
    ["Prudence", world.exposure],
    ["Voisinage", `${affected} habitant${affected > 1 ? "s semblent" : " semble"} mal en point ; ${altered ? `${altered} comportement${altered > 1 ? "s" : ""} très inquiétant${altered > 1 ? "s" : ""}.` : "la plupart suivent encore leurs habitudes."}`],
  ]
    .map(([term, description]) => `<div><dt>${term}</dt><dd>${description}</dd></div>`)
    .join("");
}

function renderSignal(snapshot) {
  const { signal, lead, player } = snapshot;
  const atSignalLocation = player.location === signal.location;
  const canListen = ["apartment", "hall"].includes(player.location) && !player.radioDays.includes(snapshot.day);
  const canSecure = player.location === "apartment" && !player.shelterSecured;
  const canRequestRefuge = player.location === "hall" && !player.refugeAccess;

  element("signal-title").textContent = signal.title;
  element("signal-description").textContent = signal.description;
  element("signal-location").textContent = signal.resolved
    ? "Signal traité pour aujourd’hui. Un autre apparaîtra demain."
    : `Lieu : ${LOCATIONS.find((location) => location.id === signal.location).name}`;
  element("signal-actions").innerHTML = [
    actionButton("signal", signal.resolved ? "Signal déjà traité" : signal.action, `${signal.minutes} min · action de quartier`, signal.resolved || !atSignalLocation),
    actionButton("radio", "Écouter la radio", "20 min · une piste narrative", !canListen),
    actionButton("secure", "Préparer l’abri", "90 min · appartement uniquement", !canSecure),
    actionButton("refuge", "Demander un refuge", "35 min · réseau nécessaire", !canRequestRefuge),
  ].join("");
  element("lead-copy").innerHTML = `<strong>${lead.title}</strong><span>${lead.description}</span>`;
}

function renderJournal(events) {
  element("event-list").innerHTML = events
    .map(
      (event) => `<li class="${event.type}"><span class="event-meta">J${event.day} · ${event.time}</span><span class="event-text">${event.text}</span></li>`,
    )
    .join("");
}

function render() {
  const snapshot = game.getSnapshot();
  element("time-display").textContent = snapshot.time;
  element("day-display").textContent = `Jour ${snapshot.day} · ${snapshot.phase.title}`;
  element("condition-display").textContent = snapshot.condition;
  renderInventory(snapshot.player);
  renderNeeds(snapshot.needs);
  renderLocation(snapshot);
  renderActions(snapshot);
  renderTravel(snapshot.player.location);
  renderWorld(snapshot);
  renderSignal(snapshot);
  renderJournal(snapshot.events);
}

function performAction(button) {
  const action = button.dataset.action;
  let result;

  switch (action) {
    case "move":
      result = game.move(button.dataset.location);
      break;
    case "wait":
      result = game.wait();
      break;
    case "drink":
      result = game.drink();
      break;
    case "eat":
      result = game.eat();
      break;
    case "sleep":
      result = game.sleep();
      break;
    case "wash":
      result = game.wash();
      break;
    case "toilet":
      result = game.useToilet();
      break;
    case "talk":
      result = game.talk();
      break;
    case "share":
      result = game.share(button.dataset.item);
      break;
    case "aid":
      result = game.requestAid();
      break;
    case "signal":
      result = game.resolveSignal();
      break;
    case "radio":
      result = game.listenRadio();
      break;
    case "secure":
      result = game.secureShelter();
      break;
    case "refuge":
      result = game.requestRefuge();
      break;
    case "work":
      result = game.work();
      break;
    case "buy":
      result = game.buy(button.dataset.item);
      break;
    case "reset":
      game.reset();
      notice.textContent = "Une nouvelle journée commence. Les rues semblent encore ordinaires.";
      render();
      return;
    default:
      return;
  }

  notice.textContent = result.message;
  render();
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled) return;
  performAction(button);
});

render();
