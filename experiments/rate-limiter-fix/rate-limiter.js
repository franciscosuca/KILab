// Token-bucket rate limiter.
// Known issues (marked with BUG) and one missing feature (marked with TODO).
// Fix all BUGs and implement the TODO without changing the public API
// (class name `RateLimiter`, and method signatures `tryRequest(key)` / `reset(key)`).

class RateLimiter {
  constructor(capacity, refillPerSecond) {
    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.buckets = new Map(); // key -> { tokens, lastRefill }
  }

  _getBucket(key) {
    if (!this.buckets.has(key)) {
      // BUG: new buckets should start FULL (capacity tokens), not empty.
      this.buckets.set(key, { tokens: 0, lastRefill: Date.now() });
    }
    return this.buckets.get(key);
  }

  _refill(bucket) {
    const now = Date.now();
    const elapsedSeconds = now - bucket.lastRefill; // BUG: Date.now() is ms, not seconds
    const refillAmount = elapsedSeconds * this.refillPerSecond;
    bucket.tokens = bucket.tokens + refillAmount; // BUG: tokens must be capped at capacity
    bucket.lastRefill = now;
  }

  tryRequest(key) {
    const bucket = this._getBucket(key);
    this._refill(bucket);

    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      return true;
    }
    return false;
  }

  // TODO: implement reset(key) that clears rate-limit history for `key`,
  // so the next tryRequest(key) call behaves as if `key` was never seen before.
}

module.exports = { RateLimiter };
