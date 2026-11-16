import assert from "node:assert/strict";
import test from "node:test";
import { PandemicSimulation } from "../simulation.js";

test("la partie commence dans la première phase avec une montre lisible", () => {
  const game = new PandemicSimulation(42);
  const snapshot = game.getSnapshot();

  assert.equal(snapshot.day, 1);
  assert.equal(snapshot.time, "07:30");
  assert.equal(snapshot.phase.title, "Signaux faibles");
  assert.equal(snapshot.player.money, 42);
});

test("les besoins sont exprimés par des ressentis après le temps écoulé", () => {
  const game = new PandemicSimulation(42);
  game.advance(5 * 60, "Test");
  const thirst = game.getNeedSignals().find((need) => need.id === "water");

  assert.notEqual(thirst.severity, "calm");
  assert.match(thirst.message, /boire|sèche/i);
});

test("l’économie se dégrade et les crédits deviennent inutiles après le basculement", () => {
  const game = new PandemicSimulation(42);
  game.advance(8 * 24 * 60, "Test de progression");
  const snapshot = game.getSnapshot();

  assert.equal(snapshot.day, 9);
  assert.equal(snapshot.phase.title, "Après le basculement");
  assert.equal(snapshot.prices.water, null);
  assert.equal(snapshot.marketOpen, false);
});

test("travailler ne rapporte plus quand les services se sont effondrés", () => {
  const game = new PandemicSimulation(42);
  game.move("workshop");
  game.advance(8 * 24 * 60, "Test de progression");
  game.player.location = "workshop";

  const result = game.work();
  assert.equal(result.ok, false);
  assert.match(result.message, /paie plus/i);
});

test("boire consomme une ressource et remet l’horloge de soif à zéro", () => {
  const game = new PandemicSimulation(42);
  game.advance(4 * 60, "Test");
  const before = game.player.inventory.water;
  const result = game.drink();
  const thirst = game.getNeedSignals().find((need) => need.id === "water");

  assert.equal(result.ok, true);
  assert.equal(game.player.inventory.water, before - 1);
  assert.equal(thirst.severity, "calm");
});
