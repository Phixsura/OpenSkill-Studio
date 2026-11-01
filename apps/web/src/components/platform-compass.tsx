"use client";
export function PlatformCompass() {
  return (<div className="rounded-2xl border-4 border-emerald-500 bg-gradient-to-br from-emerald-900/30 via-teal-900/20 to-green-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🧭</div>
    <h2 className="text-3xl font-black text-emerald-300">PLATFORM COMPASS</h2>
    <p className="text-xl font-bold text-teal-300">Bearing: TRUE NORTH · Declination: ZERO</p>
    <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
      <div className="bg-blue-500/20 rounded-lg p-2">🔼 <b className="text-blue-300">N</b> Quality</div>
      <div className="bg-orange-500/20 rounded-lg p-2">▶️ <b className="text-orange-300">E</b> Growth</div>
      <div className="bg-green-500/20 rounded-lg p-2">🔽 <b className="text-green-300">S</b> Foundation</div>
      <div className="bg-purple-500/20 rounded-lg p-2">◀️ <b className="text-purple-300">W</b> Innovation</div>
    </div>
    <p className="text-lg font-black text-emerald-300 mt-4">🧭 ALWAYS ON COURSE · NEVER STOPS!</p>
  </div>);
}
