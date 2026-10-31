"use client";
export function PlatformInfinityGauntlet() {
  const stones = ["💜Power", "💙Space", "💚Time", "❤️Reality", "🧡Soul", "💛Mind"];
  return (<div className="rounded-2xl border-4 border-yellow-500 bg-gradient-to-br from-purple-900/30 via-yellow-900/20 to-red-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🧤</div>
    <h2 className="text-3xl font-black text-yellow-300">INFINITY GAUNTLET</h2>
    <p className="text-xl font-bold text-purple-300">All Six Stones · Perfectly Balanced</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4">
      {stones.map(s => <span key={s} className="bg-white/10 rounded-full px-3 py-1 text-xs font-bold">{s}</span>)}
    </div>
    <p className="text-sm text-gray-300 mt-3">4,116 snaps · Integrity: 100% · Balance: PERFECT</p>
  </div>);
}
