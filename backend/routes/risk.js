const express = require("express");
const router = express.Router();

const { getRisk } = require("../controllers/riskController");

router.post("/predict", getRisk);

module.exports = router;