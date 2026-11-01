"use client";
export function PlatformArcanum() {
  const secrets = ["Never stop building", "Test everything", "Quality = simplicity", "DORA Elite", "Human + AI"];
  return (<div className="rounded-2xl border-4 border-purple-500 bg-gradient-to-br from-purple-900/40 via-indigo-900/30 to-blue-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">📖</div>
    <h2 className="text-3xl font-black text-purple-300">PLATFORM ARCANUM</h2>
    <p className="text-xl font-bold text-indigo-300">The Book of Secrets · Now Open to All</p>
    <div className="flex flex-wrap justify-center gap-2 mt-4 text-xs">
      {secrets.map(s => <span key={s} className="bg-purple-500/20 rounded-full px-3 py-1 font-bold">✨ {s}</span>)}
    </div>
    <p className="text-sm text-gray-300 mt-3">4,119 chapters · 907K+ pages · Binding: UNBREAKABLE</p>
  </div>);
}
