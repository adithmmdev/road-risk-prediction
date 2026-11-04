const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

function pythonExecutable() {
  if (process.env.PYTHON_EXECUTABLE) return process.env.PYTHON_EXECUTABLE;
  const local = path.join(__dirname, '../../ml-engine/.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  return fs.existsSync(local) ? local : (process.platform === 'win32' ? 'python' : 'python3');
}

exports.runPythonScript = (inputData) => new Promise((resolve, reject) => {
  const scriptPath = path.join(__dirname, '../../ml-engine/src/inference/predict_api.py');
  const timeout = Number(process.env.PYTHON_TIMEOUT_MS) || 30000;
  const child = spawn(pythonExecutable(), [scriptPath, JSON.stringify(inputData)], { timeout });
  let output = '';
  let errors = '';
  child.stdout.on('data', chunk => { output += chunk.toString(); });
  child.stderr.on('data', chunk => { errors += chunk.toString(); });
  child.on('error', reject);
  child.on('close', (code, signal) => {
    if (signal || code !== 0) {
      return reject(new Error(signal ? `Python process stopped: ${signal}` : errors || `Python exited with code ${code}`));
    }
    try {
      resolve(JSON.parse(output));
    } catch {
      reject(new Error('Invalid JSON response from Python'));
    }
  });
});
