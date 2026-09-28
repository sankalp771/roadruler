import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateSlaState, formatSlaDuration } from './sla.js';

const start = Date.parse('2026-09-01T00:00:00Z');

test('critical SLA stays green while more than half the window remains', () => {
  assert.equal(calculateSlaState(new Date(start).toISOString(), 'CRITICAL', 'RECEIVED', start + 10 * 3600000).state, 'on-track');
});

test('SLA becomes urgent below one quarter and overdue at deadline', () => {
  assert.equal(calculateSlaState(new Date(start).toISOString(), 'CRITICAL', 'RECEIVED', start + 37 * 3600000).state, 'urgent');
  assert.equal(calculateSlaState(new Date(start).toISOString(), 'CRITICAL', 'RECEIVED', start + 48 * 3600000).state, 'overdue');
});

test('escalated, pending, and resolved states do not show a live countdown', () => {
  assert.equal(calculateSlaState(null, 'CRITICAL', 'ESCALATED').state, 'escalated');
  assert.equal(calculateSlaState(null, 'PENDING', 'PROCESSING').state, 'pending');
  assert.equal(calculateSlaState(null, 'CRITICAL', 'RESOLVED').state, 'complete');
});

test('countdown formatter includes days and pads clock fields', () => {
  assert.equal(formatSlaDuration(90061000), '1d 01:01:01');
});
