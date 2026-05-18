// Stress test para Blacklist API - Entrega 4 DevOps
//
// Uso:
//   $env:BASE_URL = "http://<tu-alb-dns>.us-east-1.elb.amazonaws.com"
//   $env:STATIC_TOKEN = "<tu-token-estatico>"
//   k6 run stress/load_test.js
//
// Total: ~11 min de carga:
//   - 2 min ramp-up   0 -> 50  VUs   (verifica que el sistema arranque suave)
//   - 5 min sustain   50 VUs constante (carga sostenida)
//   - 2 min spike     50 -> 100 VUs  (pico de tráfico)
//   - 2 min ramp-down 100 -> 0  VUs  (vuelta a la calma)
//
// El propósito es generar curvas variables en New Relic para los 4 widgets:
// TRR Servicios, TRRDB, Apdex (T=0.5s), Error Rate.

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    // SLOs informativos (no fallan el test, solo se reportan)
    http_req_duration: ['p(95)<2000'],     // p95 < 2s
    http_req_failed: ['rate<0.05'],        // <5% error rate
  },
};

const BASE = __ENV.BASE_URL;
const TOKEN = __ENV.STATIC_TOKEN;

if (!BASE || !TOKEN) {
  throw new Error('Faltan variables: BASE_URL y/o STATIC_TOKEN');
}

const APP_UUID = '550e8400-e29b-41d4-a716-446655440000';

export default function () {
  const headers = {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  // 1) Health check (sin auth)
  const healthRes = http.get(`${BASE}/health`);
  check(healthRes, { 'health 200': (r) => r.status === 200 });

  // 2) POST blacklist con email único
  const email = `vu${__VU}-iter${__ITER}-${Math.random().toString(36).slice(2, 8)}@stress.test`;
  const postPayload = JSON.stringify({
    email,
    app_uuid: APP_UUID,
    blocked_reason: `stress test VU${__VU}`,
  });
  const postRes = http.post(`${BASE}/blacklists`, postPayload, { headers });
  check(postRes, { 'post 201': (r) => r.status === 201 });

  // 3) GET blacklist del email recién creado
  const getRes = http.get(`${BASE}/blacklists/${email}`, { headers });
  check(getRes, { 'get 200': (r) => r.status === 200 });

  sleep(1);
}
