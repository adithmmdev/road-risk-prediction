const express = require("express");
const cors = require("cors");

const riskRoutes = require("./routes/risk");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/risk", riskRoutes);

app.listen(5000, () => {
  console.log("Server running on port 5000");
});