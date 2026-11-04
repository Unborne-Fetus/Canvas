import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
assert.match(html, /<title>Canvas — Fakémon Sprite Studio<\/title>/);
assert.match(html, /<canvas width="64" height="64" id="artboard"/);
assert.match(html, /id="preview"[^>]*width="64" height="64"/);
for (const tool of ['pencil','eraser','bucket','eyedropper','line','rect','rectfill','ellipse','ellipsefill','select']) {
  assert.ok(html.includes('data-tool="'+tool+'"'), 'Missing tool: '+tool);
}
for (const feature of ['function fill(', 'function exportPng(', 'function undo(', 'function redo(', 'function fromProject(', 'function toProject(', 'function addLayer(', 'function pasteSelection(', "localStorage.setItem("]) {
  assert.ok(html.includes(feature),'Missing feature: '+feature);
}
for (const feature of ['function livePoll(', 'function connectLive(', 'function liveApplyProject(', 'canvas-live-backup:', 'raw.githubusercontent.com/Unborne-Fetus/Canvas/main/', 'id="liveApply"', 'id="liveDisconnect"']) {
  assert.ok(html.includes(feature),'Missing AI Live feature: '+feature);
}
for (const feature of ['id="refsBtn"', 'id="refsDialog"', 'function refsLoad(', 'function refAddFrame(', 'id="refsCategory"']) {
  assert.ok(html.includes(feature), 'Missing local reference library UI: ' + feature);
}
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,'Missing editor script');
new vm.Script(match[1],{filename:'canvas-editor.js'});
console.log('Canvas smoke test passed: 64×64 editor, AI Live sync hooks, and JavaScript syntax.');
