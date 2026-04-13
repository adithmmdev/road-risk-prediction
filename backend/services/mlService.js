const { runPythonScript } = require("../utils/runPython");

exports.runMLModel = async (inputData) => {
  const result = await runPythonScript(inputData);
  return result;
};