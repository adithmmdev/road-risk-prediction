import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import { useEffect, useState, useRef } from "react";

function App() {
  const [geoData, setGeoData] = useState(null);
  const [riskMap, setRiskMap] = useState({});
  const selectedLayerRef = useRef(null); // track selected road

  // =========================================
  // LOAD GEOJSON
  // =========================================
  useEffect(() => {
    fetch("/chennai_roads.geojson")
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error("GeoJSON load error:", err));
  }, []);

  // =========================================
  // COLOR LOGIC
  // =========================================
  const getColor = (risk) => {
    if (risk > 70) return "#e53935"; // red
    if (risk > 35) return "#fb8c00"; // orange
    return "#43a047"; // green
  };

  // =========================================
  // 🧠 ADVANCED EXPLANATION ENGINE
  // =========================================
  const explainRisk = (r) => {
    if (!r) return "No data available";

    let reasons = [];

    // Geometry
    if (r.geometry_risk > 70)
      reasons.push("complex road structure (curves/intersections)");
    else if (r.geometry_risk < 30)
      reasons.push("simple road layout");

    // ML conditions
    if (r.ml_risk > 70)
      reasons.push("harsh environmental conditions");
    else if (r.ml_risk < 30)
      reasons.push("favorable driving conditions");

    // Time
    if (r.hour >= 22 || r.hour < 6)
      reasons.push("night-time low visibility");

    // Weather
    if (r.weather === "Rain")
      reasons.push("wet roads increase accident risk");
    if (r.weather === "Fog")
      reasons.push("fog reduces visibility");
    if (r.weather === "Storm")
      reasons.push("storm conditions are dangerous");

    return reasons.length
      ? "Risk influenced by: " + reasons.join(", ")
      : "Stable road conditions";
  };

  // =========================================
  // 🕒 TIME FORMATTER (CORRECT)
  // =========================================
  const formatTime = (hour) => {
    const hour12 = hour % 12 || 12;
    const ampm = hour >= 12 ? "PM" : "AM";
    return `${hour12}:00 ${ampm}`;
  };

  // =========================================
  // ROAD CLICK HANDLER
  // =========================================
  const onEachFeature = (feature, layer) => {
    const roadId = feature.properties.road_id;
    const roadName = feature.properties.name || "Unnamed Road";

    layer.on("click", async () => {
      try {
        let r = riskMap[roadId];

        // =========================================
        // FETCH ONLY IF NOT CACHED
        // =========================================
        if (!r) {
          const response = await axios.post(
            "http://localhost:5000/api/risk/predict",
            {
              road_index: roadId % 500000,
            }
          );

          r = response.data;

          setRiskMap((prev) => ({
            ...prev,
            [roadId]: r,
          }));
        }

        const color = getColor(r.final_risk);

        // =========================================
        // RESET PREVIOUS ROAD
        // =========================================
        if (selectedLayerRef.current) {
          selectedLayerRef.current.setStyle({
            color: "blue",
            weight: 2,
          });
        }

        // =========================================
        // HIGHLIGHT CURRENT ROAD
        // =========================================
        layer.setStyle({
          color: color,
          weight: 6,
          opacity: 1,
        });

        selectedLayerRef.current = layer;

        // =========================================
        // FORMAT TIME
        // =========================================
        const formattedTime = formatTime(r.hour);

        // =========================================
        // POPUP UI
        // =========================================
        layer.bindPopup(`
          <div style="font-family: Arial; font-size: 14px; line-height:1.5;">
            <b style="font-size:16px;">${roadName}</b><br/>
            <b style="color:${color}; font-size:15px;">
              ${r.risk_tier}
            </b><br/><br/>

            🌦️ Weather: ${r.weather}<br/>
            🌡️ Temp: ${r.temperature}°C<br/>
            🕒 Time: ${formattedTime}<br/><br/>

            <b>ML Risk:</b> ${r.ml_risk}<br/>
            <b>Geometry Risk:</b> ${r.geometry_risk}<br/>
            <b>Final Risk:</b> ${r.final_risk}<br/><br/>

            <i style="color:#555;">
              ${explainRisk(r)}
            </i>
          </div>
        `).openPopup();

      } catch (err) {
        console.error("Prediction error:", err);

        layer.bindPopup("⚠️ Prediction failed").openPopup();
      }
    });
  };

  // =========================================
  // RENDER
  // =========================================
  return (
    <div>
      <h2 style={{ textAlign: "center", margin: "10px" }}>
        🚦 Chennai Smart Road Risk Map
      </h2>

      <MapContainer
        center={[13.0827, 80.2707]}
        zoom={13}
        style={{ height: "90vh", width: "100%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {geoData && (
          <GeoJSON
            data={geoData}
            style={() => ({
              color: "blue",
              weight: 2,
            })}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
    </div>
  );
}

export default App;