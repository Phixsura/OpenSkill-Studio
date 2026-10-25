"use client";
export function PlatformNirvana() {
  return (<div className="rounded-2xl border-4 border-pink-300 bg-gradient-to-br from-pink-900/20 via-purple-900/20 to-indigo-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🪷</div>
    <h2 className="text-3xl font-black text-pink-300">PLATFORM NIRVANA</h2>
    <p className="text-xl font-bold text-purple-300">Enlightenment Complete · Suffering Ceased</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {["Bugs ❌", "Downtime ❌", "Failures ❌", "Debt ❌", "Complexity ❌"].map(s =>
        <span key={s} className="bg-green-500/20 rounded-full px-3 py-1 font-bold">{s}</span>
      )}
    </div>
    <p className="text-lg font-bold text-pink-300 mt-3">🕉️ Commit. Test. Push. Repeat.</p>
  </div>);
}
