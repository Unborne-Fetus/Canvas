import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

function load(relativePath) {
  return JSON.parse(readFileSync(new URL('../' + relativePath, import.meta.url), 'utf8'));
}

const reference = load('ai/contracts/reference.schema.json');
const training = load('ai/contracts/training-request.schema.json');
const generation = load('ai/contracts/generation-request.schema.json');
for (const schema of [reference, training, generation]) {
  assert.equal(schema.$schema, 'https://json-schema.org/draft/2020-12/schema');
  assert.equal(schema.type, 'object');
  assert.equal(schema.additionalProperties, false);
  assert.ok(schema.required.length > 0);
}
assert.ok(reference.required.includes('permissions'));
for (const flag of ['reference', 'train', 'redistribute']) {
  assert.ok(reference.properties.permissions.required.includes(flag));
}
assert.equal(training.properties.image_size.const, 64);
assert.equal(generation.properties.image_size.const, 64);
assert.ok(training.properties.mode.enum.includes('from_scratch'));
assert.ok(training.properties.mode.enum.includes('fine_tune'));
assert.equal(generation.properties.count.maximum, 4);
const architecture = readFileSync(new URL('../docs/AI_STUDIO_ARCHITECTURE.md', import.meta.url), 'utf8');
for (const feature of ['AI Studio', 'reference', 'training', 'generation', '64×64', 'Mega Scizor Y']) {
  assert.ok(architecture.toLowerCase().includes(feature.toLowerCase()), 'Architecture missing: ' + feature);
}
console.log('AI Studio blueprint and JSON contract structural smoke checks passed.');
