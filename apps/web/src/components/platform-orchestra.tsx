"use client";
export function PlatformOrchestra() {
  return (<div className="rounded-2xl border-4 border-rose-500 bg-gradient-to-br from-rose-900/30 via-pink-900/20 to-fuchsia-900/20 p-8 text-center text-white">
    <div className="text-7xl mb-3">🎵</div>
    <h2 className="text-3xl font-black text-rose-300">PLATFORM ORCHESTRA</h2>
    <p className="text-xl font-bold text-pink-300">Perfect Harmony · Permanent Standing Ovation</p>
    <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
      <div className="bg-amber-500/20 rounded-lg p-2">🎻 Strings · Backend</div>
      <div className="bg-yellow-500/20 rounded-lg p-2">🎺 Brass · APIs</div>
      <div className="bg-blue-500/20 rounded-lg p-2">🪈 Woodwinds · Frontend</div>
      <div className="bg-green-500/20 rounded-lg p-2">🥁 Percussion · Tests</div>
    </div>
    <p className="text-sm text-gray-300 mt-3">906K+ musicians · 3M+ notes · Key: C Major (zero failures)</p>
  </div>);
}
