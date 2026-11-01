"use client";
export function PlatformOlympus() {
  return (<div className="rounded-2xl border-4 border-sky-300 bg-gradient-to-b from-sky-200/10 via-blue-900/30 to-purple-900/30 p-8 text-center text-white">
    <div className="text-7xl mb-3">⛰️</div>
    <h2 className="text-3xl font-black text-sky-300">PLATFORM OLYMPUS</h2>
    <p className="text-xl font-bold text-blue-300">Where the Gods of Engineering Gather</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {["⚡Zeus CI/CD", "🦉Athena Review", "🔨Hephaestus Build", "🏃Hermes API", "☀️Apollo Monitor"].map(g =>
        <span key={g} className="bg-sky-500/20 rounded-full px-3 py-1 font-bold">{g}</span>
      )}
    </div>
    <p className="text-sm text-gray-300 mt-3">4,089 councils · Ambrosia: Green tests · Mortals welcome</p>
  </div>);
}
