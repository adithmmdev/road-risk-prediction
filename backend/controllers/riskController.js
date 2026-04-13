const axios = require("axios");
const { runPythonScript } = require("../utils/runPython");

exports.getRisk = async (req, res) => {
  try {
    const { road_index } = req.body;

    // =========================================
    // 🕒 REAL TIME (SYSTEM)
    // =========================================
    const now = new Date();

    const hour = now.getHours();
    const is_weekend = [0, 6].includes(now.getDay()) ? 1 : 0;

    // =========================================
    // 🌦️ LIVE WEATHER (OPEN-METEO)
    // =========================================
    const weatherRes = await axios.get(
      "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true"
    );

    const weatherData = weatherRes.data.current_weather;

    // =========================================
    // 🌦️ MAP WEATHER CODE → ML FORMAT
    // =========================================
    let weather_type = "Clear";

    if (weatherData.weathercode >= 51 && weatherData.weathercode < 71) {
      weather_type = "Rain";
    } else if (weatherData.weathercode >= 71 && weatherData.weathercode < 95) {
      weather_type = "Snow";
    } else if (weatherData.weathercode >= 95) {
      weather_type = "Storm";
    }

    // =========================================
    // 🧠 BUILD ML INPUT
    // =========================================
    const inputData = {
      road_index: road_index,

      visibility: 10, // fallback (can improve later)
      temperature: weatherData.temperature,
      humidity: 70, // fallback

      weather: weather_type,
      hour: hour,
      is_weekend: is_weekend,
    };

    // =========================================
    // 🤖 CALL PYTHON MODEL
    // =========================================
    const result = await runPythonScript(inputData);
    result.weather=weather_type;
    result.temperature=weatherData.temperature;
    result.hour=hour;

    // =========================================
    // RESPONSE
    // =========================================
    res.json(result);

  } catch (error) {
    console.error("Backend Error:", error.message);
    res.status(500).json({
      error: "Risk prediction failed",
    });
  }
};