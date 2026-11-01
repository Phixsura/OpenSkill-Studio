"use client";
export function PlatformPrism() {
  const colors = [
    { name: "Backend", color: "bg-red-500/30 text-red-300" },
    { name: "APIs", color: "bg-orange-500/30 text-orange-300" },
    { name: "Frontend", color: "bg-yellow-500/30 text-yellow-300" },
    { name: "Tests", color: "bg-green-500/30 text-green-300" },
    { name: "Docs", color: "bg-blue-500/30 text-blue-300" },
    { name: "Security", color: "bg-indigo-500/30 text-indigo-300" },
    { name: "Observability", color: "bg-purple-500/30 text-purple-300" },
  ];
  return (<div className="rounded-2xl border-4 border-sky-500 bg-gradient-to-br from-gray-900/60 to-sky-900/30 p-8 text-center text-white">
    <div className="text-7xl mb-3">🔷</div>
    <h2 className="text-3xl font-black text-sky-300">PLATFORM PRISM</h2>
    <p className="text-lg font-bold text-gray-300">Full Spectrum Dispersion · Every Wavelength Represented</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4">
      {colors.map(c => <span key={c.name} className={`${c.color} rounded-full px-3 py-1 text-xs font-bold`}>{c.name}</span>)}
    </div>
    <p className="text-sm text-gray-400 mt-3">Refraction index: 4,021 · 906K+ stellar objects</p>
  </div>);
}
