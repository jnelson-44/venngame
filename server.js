const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, "public")));

const db = new sqlite3.Database(path.join(__dirname, "intersection.db"));

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS solves (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      puzzle_id TEXT NOT NULL,
      solve_time_seconds INTEGER NOT NULL,
      solved_at TEXT NOT NULL
    )
  `);
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.get("/api/puzzle", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "puzzleData.json"));
});

app.get("/api/stats/:puzzleId", (req, res) => {
  const { puzzleId } = req.params;

  db.get(
    `
    SELECT
      COUNT(*) AS playersSolved,
      AVG(solve_time_seconds) AS averageTime
    FROM solves
    WHERE puzzle_id = ?
    `,
    [puzzleId],
    (err, row) => {
      if (err) {
        res.status(500).json({ error: "Database error" });
        return;
      }

      res.json({
        playersSolved: row.playersSolved || 0,
        averageTime: row.averageTime ? Math.round(row.averageTime) : 0
      });
    }
  );
});

app.post("/api/solve", (req, res) => {
  const { puzzleId, solveTimeSeconds } = req.body;

  if (!puzzleId || solveTimeSeconds == null) {
    res.status(400).json({ error: "Missing data" });
    return;
  }

  const solvedAt = new Date().toISOString();

  db.run(
    `
    INSERT INTO solves (puzzle_id, solve_time_seconds, solved_at)
    VALUES (?, ?, ?)
    `,
    [puzzleId, solveTimeSeconds, solvedAt],
    function (err) {
      if (err) {
        res.status(500).json({ error: "Insert failed" });
        return;
      }

      res.json({ success: true });
    }
  );
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});