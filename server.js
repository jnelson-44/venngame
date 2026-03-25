const express = require("express");
const path = require("path");
const cors = require("cors");
const { Pool } = require("pg");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV !== "development" && process.env.DATABASE_URL
    ? { rejectUnauthorized: false }
    : false
});

async function initDb() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS solves (
      id SERIAL PRIMARY KEY,
      puzzle_id TEXT NOT NULL,
      solve_time_seconds INTEGER NOT NULL,
      solved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `);
}

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.get("/api/puzzle", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "puzzleData.json"));
});

app.get("/api/stats/:puzzleId", async (req, res) => {
  const { puzzleId } = req.params;

  try {
    const result = await pool.query(
      `
      SELECT
        COUNT(*)::int AS "playersSolved",
        ROUND(AVG(solve_time_seconds))::int AS "averageTime"
      FROM solves
      WHERE puzzle_id = $1
      `,
      [puzzleId]
    );

    const row = result.rows[0] || {};

    res.json({
      playersSolved: row.playersSolved || 0,
      averageTime: row.averageTime || 0
    });
  } catch (err) {
    console.error("Stats query failed:", err);
    res.status(500).json({ error: "Database error" });
  }
});

app.post("/api/solve", async (req, res) => {
  const { puzzleId, solveTimeSeconds } = req.body;

  if (!puzzleId || solveTimeSeconds == null) {
    res.status(400).json({ error: "Missing data" });
    return;
  }

  try {
    await pool.query(
      `
      INSERT INTO solves (puzzle_id, solve_time_seconds)
      VALUES ($1, $2)
      `,
      [puzzleId, solveTimeSeconds]
    );

    res.json({ success: true });
  } catch (err) {
    console.error("Insert failed:", err);
    res.status(500).json({ error: "Insert failed" });
  }
});

initDb()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("Failed to initialize database:", err);
    process.exit(1);
  });