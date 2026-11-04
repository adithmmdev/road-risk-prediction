require("dotenv").config();
const express = require("express");
const cors = require("cors");

const riskRoutes = require("./routes/risk");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/risk", riskRoutes);

const port = process.env.PORT || 5000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
