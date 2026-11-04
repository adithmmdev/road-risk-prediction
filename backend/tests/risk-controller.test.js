const test = require('node:test');
const assert = require('node:assert/strict');
const axios = require('axios');
const bridge = require('../utils/runPython');

function response() {
  return { code: 200, body: null, status(code) { this.code = code; return this; }, json(body) { this.body = body; return this; } };
}

test('rejects invalid road indexes before weather or inference', async () => {
  const { getRisk } = require('../controllers/riskController');
  for (const value of [-1, 0.5, '1', null, true, undefined]) {
    const res = response();
    await getRisk({ body: { road_index: value } }, res);
    assert.equal(res.code, 400);
  }
});

test('converts Celsius weather to model Fahrenheit and keeps Celsius in the response', async () => {
  const originalGet = axios.get;
  const originalRun = bridge.runPythonScript;
  const modulePath = require.resolve('../controllers/riskController');
  let input;
  axios.get = async (url, options) => {
    assert.ok(options.timeout > 0);
    return { data: { current_weather: { temperature: 30, weathercode: 45 } } };
  };
  bridge.runPythonScript = async value => { input = value; return { final_risk: 20, risk_tier: 'LOW' }; };
  delete require.cache[modulePath];
  try {
    const res = response();
    await require(modulePath).getRisk({ body: { road_index: 0 } }, res);
    assert.equal(res.code, 200);
    assert.equal(input.temperature, 86);
    assert.equal(input.weather, 'Fog');
    assert.ok(input.hour >= 0 && input.hour <= 23);
    assert.equal(res.body.temperature, 30);
  } finally {
    axios.get = originalGet;
    bridge.runPythonScript = originalRun;
    delete require.cache[modulePath];
  }
});
