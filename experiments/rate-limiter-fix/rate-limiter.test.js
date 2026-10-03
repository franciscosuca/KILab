// Fixed test suite — do not let the model under test edit this file.
const test = require('node:test');
const assert = require('node:assert/strict');
const { RateLimiter } = require('./rate-limiter');

test('new key starts with a full bucket (capacity requests succeed immediately)', () => {
  const rl = new RateLimiter(3, 1);
  assert.equal(rl.tryRequest('a'), true);
  assert.equal(rl.tryRequest('a'), true);
  assert.equal(rl.tryRequest('a'), true);
  assert.equal(rl.tryRequest('a'), false); // 4th immediate request should fail
});

test('refill is time-based in seconds, not milliseconds', async () => {
  const rl = new RateLimiter(1, 1); // 1 token/sec refill
  assert.equal(rl.tryRequest('b'), true);
  assert.equal(rl.tryRequest('b'), false);
  await new Promise((r) => setTimeout(r, 1100));
  assert.equal(rl.tryRequest('b'), true); // refilled after ~1s
});

test('tokens never exceed capacity even after long idle', async () => {
  const rl = new RateLimiter(2, 100); // fast refill for test speed
  await new Promise((r) => setTimeout(r, 50));
  assert.equal(rl.tryRequest('c'), true);
  assert.equal(rl.tryRequest('c'), true);
  assert.equal(rl.tryRequest('c'), false); // capacity is 2, bucket must not overflow
});

test('different keys are independent', () => {
  const rl = new RateLimiter(1, 1);
  assert.equal(rl.tryRequest('x'), true);
  assert.equal(rl.tryRequest('y'), true);
});

test('reset(key) clears history for that key only', () => {
  const rl = new RateLimiter(1, 1);
  assert.equal(rl.tryRequest('z'), true);
  assert.equal(rl.tryRequest('z'), false);
  rl.reset('z');
  assert.equal(rl.tryRequest('z'), true);
});
