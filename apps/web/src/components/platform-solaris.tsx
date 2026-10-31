"use client";
export function PlatformSolaris() {
  return (<div className="rounded-2xl border-4 border-yellow-500 bg-gradient-to-br from-yellow-900/20 via-orange-900/20 to-red-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">☀️</div>
    <h2 className="text-3xl font-black text-yellow-300">PLATFORM SOLARIS</h2>
    <p className="text-xl font-bold text-orange-300">Entire Solar System · Gravitationally Stable</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {["SDK", "Marketplace", "Automation", "Portal", "Security", "Infra", "Observability"].map(p =>
        <span key={p} className="bg-yellow-500/20 rounded-full px-3 py-1 font-bold">🪐 {p}</span>
      )}
    </div>
    <p className="text-sm text-gray-300 mt-3">906K+ moons · Dark matter: ZERO · Habitable: EVERYWHERE</p>
  </div>);
}
