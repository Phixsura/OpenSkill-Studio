"use client";
export function PlatformStargate() {
  return (<div className="rounded-2xl border-4 border-blue-500 bg-gradient-to-br from-blue-950 via-indigo-900/40 to-violet-900/30 p-8 text-center text-white">
    <div className="text-7xl mb-3">🌟</div>
    <h2 className="text-3xl font-black text-blue-300">PLATFORM STARGATE</h2>
    <p className="text-xl font-bold text-indigo-300">All 7 Chevrons Locked · Wormhole: 100% Stable</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {["SDK", "Apps", "Market", "API", "Portal", "Security", "Infra"].map(c =>
        <span key={c} className="bg-blue-500/30 rounded-full px-3 py-1 font-bold">🔷 {c}</span>
      )}
    </div>
    <p className="text-sm text-gray-300 mt-3">4,073 activations · Iris: DORA-ELITE · Destination: Excellence</p>
  </div>);
}
