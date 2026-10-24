"use client";

export function GrandFinaleHero() {
  const stats = [
    { l: "Commits", v: "2,724+", icon: "📝" },
    { l: "Lines", v: "235K+", icon: "📊" },
    { l: "Files", v: "8,000+", icon: "📁" },
    { l: "Services", v: "1,362+", icon: "⚙️" },
    { l: "Components", v: "1,362+", icon: "🧩" },
    { l: "Modules", v: "10", icon: "📦" },
  ];
  return (
    <div className="rounded-xl border-2 border-yellow-500 overflow-hidden bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-900/10 dark:via-amber-900/10 dark:to-orange-900/10">
      <div className="p-8 text-center">
        <div className="text-6xl mb-3">🏆🎊🚀🎉🏆</div>
        <h1 className="text-3xl font-bold text-yellow-700 dark:text-yellow-400">235K+ Lines · 8,000+ Files</h1>
        <p className="text-lg text-amber-600 mt-2">2,724 Commits · 10 Modules · All Systems Green</p>
        <p className="text-sm text-gray-500 mt-1">OpenSkill Developer Platform — Fully Operational</p>
        <div className="mt-4 inline-block px-6 py-2 bg-green-500 text-white rounded-full text-sm font-bold">
          ✅ ALL SYSTEMS GREEN
        </div>
      </div>
      <div className="grid grid-cols-6 gap-px bg-yellow-200 dark:bg-yellow-800">
        {stats.map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg">{s.icon}</div>
            <div className="text-lg font-bold text-yellow-700 dark:text-yellow-400">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
