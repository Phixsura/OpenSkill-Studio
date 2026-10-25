"use client";
export function PlatformSentinel() {
  return (<div className="rounded-2xl border-4 border-green-600 bg-gradient-to-br from-green-900/30 via-emerald-900/20 to-teal-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🛡️</div>
    <h2 className="text-3xl font-black text-green-300">PLATFORM SENTINEL</h2>
    <p className="text-xl font-bold text-emerald-300">Eternal Vigilance · Zero Breaches</p>
    <div className="flex justify-center gap-3 mt-4 text-sm">
      <div className="bg-blue-500/20 rounded-lg px-3 py-2">📡 Pytest radar</div>
      <div className="bg-gray-500/20 rounded-lg px-3 py-2">🛡️ Type armor</div>
      <div className="bg-orange-500/20 rounded-lg px-3 py-2">⚡ CI/CD weapon</div>
    </div>
    <p className="text-sm text-gray-300 mt-3">4,052 watches · Alert: GREEN · Shift: ETERNAL</p>
  </div>);
}
