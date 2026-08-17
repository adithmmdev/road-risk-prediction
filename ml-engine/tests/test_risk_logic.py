import unittest

from src.inference.risk_logic import classify_risk, fuse_risk


class RiskLogicTests(unittest.TestCase):
    def test_low_boundary(self):
        self.assertEqual(classify_risk(34.99), "LOW")

    def test_medium_boundaries(self):
        self.assertEqual(classify_risk(35), "MEDIUM")
        self.assertEqual(classify_risk(69.99), "MEDIUM")

    def test_high_boundary(self):
        self.assertEqual(classify_risk(70), "HIGH")

    def test_fusion_uses_documented_weights(self):
        score, tier = fuse_risk(80, 60)
        self.assertEqual(score, 73.0)
        self.assertEqual(tier, "HIGH")

    def test_invalid_ml_score(self):
        with self.assertRaises(ValueError):
            fuse_risk(-1, 50)

    def test_invalid_geometry_score(self):
        with self.assertRaises(ValueError):
            fuse_risk(50, 101)


if __name__ == "__main__":
    unittest.main()
