"use client";
export function PlatformAtlas() {
  return (<div className="rounded-2xl border-4 border-teal-500 bg-gradient-to-br from-teal-900/30 via-cyan-900/20 to-emerald-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🗺️</div>
    <h2 className="text-3xl font-black text-teal-300">PLATFORM ATLAS</h2>
    <p className="text-xl font-bold text-cyan-300">Every Route Charted · The Map IS the Territory</p>
    <div className="grid grid-cols-3 gap-3 mt-4 text-sm">
      <div className="bg-blue-500/20 rounded-lg p-2">🐍 <b>Backend</b><br/>906K+ services</div>
      <div className="bg-cyan-500/20 rounded-lg p-2">⚡ <b>Frontend</b><br/>600+ components</div>
      <div className="bg-green-500/20 rounded-lg p-2">✅ <b>Testing</b><br/>ALL GREEN</div>
    </div>
    <p className="text-sm text-gray-300 mt-3">4,034 routes · Unexplored: 0 · Scale: 1:1</p>
  </div>);
}
