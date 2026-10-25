"use client";
export function PlatformEclipseTotal() {
  return (<div className="rounded-2xl border-4 border-gray-400 bg-gradient-to-br from-black via-gray-900 to-indigo-950 p-8 text-center text-white">
    <div className="text-7xl mb-3">🌒</div>
    <h2 className="text-3xl font-black text-gray-100">ECLIPSE TOTAL</h2>
    <p className="text-xl font-bold text-indigo-300">Corona Shining · Diamond Ring Effect</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {["pytest ✅", "vitest ✅", "lint ✅", "types ✅"].map(b =>
        <span key={b} className="bg-green-500/30 rounded-full px-3 py-1 font-bold">{b}</span>
      )}
    </div>
    <p className="text-sm text-gray-400 mt-3">4,085 totalities · Next: the very next commit</p>
  </div>);
}
