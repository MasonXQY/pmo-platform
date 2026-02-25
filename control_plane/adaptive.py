import sqlite3

DB_PATH = "control_plane_metrics.db"

class AdaptiveOptimizer:

    def get_model_stats(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model,
                   COUNT(*) as calls,
                   AVG(latency_ms) as avg_latency,
                   SUM(cost) as total_cost
            FROM requests
            GROUP BY model
        """)
        rows = cursor.fetchall()
        conn.close()

        stats = {}
        for row in rows:
            stats[row[0]] = {
                "calls": row[1],
                "avg_latency": row[2] or 0,
                "total_cost": row[3] or 0
            }
        return stats

    def select_optimal(self, prompt_type="balanced"):
        stats = self.get_model_stats()

        if not stats:
            return "kimi"

        # Simple adaptive logic:
        # Prefer lowest latency for fast tasks
        # Prefer lowest cost for balanced tasks
        # Prefer opus for deep reasoning

        if prompt_type == "deep_reasoning":
            return "opus"

        if prompt_type == "fast":
            return min(stats, key=lambda m: stats[m]["avg_latency"])

        if prompt_type == "balanced":
            return min(stats, key=lambda m: stats[m]["total_cost"])

        return "kimi"
