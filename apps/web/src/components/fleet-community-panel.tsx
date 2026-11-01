"use client";
export function FleetCommunityPanel({ stars, forks, contributors, score, vibrant }: { stars: number; forks: number; contributors: number; score: number; vibrant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Community</h3>
    <div className="text-sm">⭐ {stars.toLocaleString()} · 🍴 {forks} · 👥 {contributors}</div>
    <div className={`text-xs ${vibrant ? "text-green-600" : "text-yellow-600"}`}>{vibrant ? "✅ Vibrant" : "⚠️ Needs growth"}</div>
  </div>);
}
