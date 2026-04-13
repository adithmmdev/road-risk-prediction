const { spawn } = require("child_process");
const path = require("path");

exports.runPythonScript = (inputData) => {
  return new Promise((resolve, reject) => {

    // ✅ 1. Path to YOUR virtual environment Python
    const pythonPath = path.join(
      __dirname,
      "../../ml-engine/.venv/Scripts/python.exe"
    );

    // ✅ 2. Path to your ML API script
    const scriptPath = path.join(
      __dirname,
      "../../ml-engine/src/inference/predict_api.py"
    );

    // ✅ 3. Run Python
    const python = spawn(pythonPath, [
      scriptPath,
      JSON.stringify(inputData),
    ]);

    let data = "";
    let error = "";

    // Capture output
    python.stdout.on("data", (chunk) => {
      data += chunk.toString();
    });

    // Capture errors
    python.stderr.on("data", (chunk) => {
      error += chunk.toString();
    });

    // On finish
    python.on("close", (code) => {
      if (code !== 0) {
        console.error("Python Error:", error);
        return reject(error);
      }

      try {
        const result = JSON.parse(data);
        resolve(result);
      } catch (err) {
        console.error("Invalid JSON:", data);
        reject("Invalid response from Python");
      }
    });
  });
};