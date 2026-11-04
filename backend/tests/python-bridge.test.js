const test = require('node:test');
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const childProcess = require('node:child_process');
const { PassThrough } = require('node:stream');

async function withProcess(run) {
  const original = childProcess.spawn;
  let invocation;
  const child = new EventEmitter();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  childProcess.spawn = (...args) => { invocation = args; return child; };
  const modulePath = require.resolve('../utils/runPython');
  delete require.cache[modulePath];
  try {
    await run(require(modulePath).runPythonScript, child, () => invocation);
  } finally {
    childProcess.spawn = original;
    delete require.cache[modulePath];
    delete process.env.PYTHON_EXECUTABLE;
  }
}

test('passes the interpreter override, script path and JSON input without a shell', async () => {
  await withProcess(async (run, child, invocation) => {
    process.env.PYTHON_EXECUTABLE = '/custom/python';
    const result = run({ road_index: 2 });
    assert.equal(invocation()[0], '/custom/python');
    assert.match(invocation()[1][0], /predict_api\.py$/);
    assert.deepEqual(JSON.parse(invocation()[1][1]), { road_index: 2 });
    assert.ok(invocation()[2].timeout > 0);
    assert.equal(invocation()[2].shell, undefined);
    child.stdout.write('{"risk_tier":"LOW"}');
    child.emit('close', 0, null);
    assert.deepEqual(await result, { risk_tier: 'LOW' });
  });
});

test('rejects an interpreter launch failure', async () => {
  await withProcess(async (run, child) => {
    const result = assert.rejects(run({}), /not found/);
    child.emit('error', new Error('interpreter not found'));
    await result;
  });
});

test('rejects nonzero exits and invalid output', async () => {
  await withProcess(async (run, child) => {
    const result = assert.rejects(run({}), /Missing model/);
    child.stderr.write('Missing model');
    child.emit('close', 1, null);
    await result;
  });
  await withProcess(async (run, child) => {
    const result = assert.rejects(run({}), /Invalid JSON/);
    child.stdout.write('not json');
    child.emit('close', 0, null);
    await result;
  });
});

test('reports a timed-out or terminated process', async () => {
  await withProcess(async (run, child) => {
    const result = assert.rejects(run({}), /SIGTERM/);
    child.emit('close', null, 'SIGTERM');
    await result;
  });
});
