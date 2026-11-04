const axios = require("axios");
const { runPythonScript } = require("../utils/runPython");

exports.getRisk = async (req, res) => {
  try {
    const { road_index } = req.body;
    if (!Number.isInteger(road_index) || road_index < 0) {
      return res.status(400).json({ error: "road_index must be a non-negative integer" });
    }

    // 🕒 REAL TIME (SYSTEM)
    const now = new Date();

    const hour = Number(new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', hour: '2-digit', hourCycle: 'h23' }).format(now));
    const weekday = new Intl.DateTimeFormat('en-US', { timeZone: 'Asia/Kolkata', weekday: 'short' }).format(now);
    const is_weekend = ['Sat', 'Sun'].includes(weekday) ? 1 : 0;

    // 🌦️ LIVE WEATHER (OPEN-METEO)
    const weatherRes = await axios.get(
      "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true",
      { timeout: 10000 }
    );

    const weatherData = weatherRes.data.current_weather;

    // 🌦️ MAP WEATHER CODE → ML FORMAT
    let weather_type = "Clear";

    if ([45, 48].includes(weatherData.weathercode)) {
      weather_type = "Fog";
    } else if (weatherData.weathercode >= 51 && weatherData.weathercode < 71) {
      weather_type = "Rain";
    } else if (weatherData.weathercode >= 71 && weatherData.weathercode < 95) {
      weather_type = "Snow";
    } else if (weatherData.weathercode >= 95) {
      weather_type = "Storm";
    }

    const inputData = {
      road_index: road_index,

      visibility: 10, // fallback (can improve later)
      temperature: weatherData.temperature * 9 / 5 + 32,
      humidity: 70, // fallback

      weather: weather_type,
      hour: hour,
      is_weekend: is_weekend,
    };

    const result = await runPythonScript(inputData);
    result.weather=weather_type;
    result.temperature=weatherData.temperature;
    result.hour=hour;

    // RESPONSE
    res.json(result);

  } catch (error) {
    console.error("Backend Error:", error.message);
    res.status(500).json({
      error: "Risk prediction failed",
    });
  }
};
