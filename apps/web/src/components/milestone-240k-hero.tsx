"use client";

export function Milestone240kHero() {
  const stats = [
    { l: "Commits", v: "2,784+", icon: "📝" },
    { l: "Lines", v: "240K+", icon: "📊" },
    { l: "Files", v: "8,228+", icon: "📁" },
    { l: "Services", v: "1,392+", icon: "⚙️" },
    { l: "Components", v: "1,392+", icon: "🧩" },
    { l: "Modules", v: "10", icon: "📦" },
  ];
  return (
    <div className="rounded-xl border-4 border-yellow-500 overflow-hidden bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-900/10 dark:via-amber-900/10 dark:to-orange-900/10">
      <div className="p-10 text-center">
        <div className="text-6xl mb-4">🏆🎊🚀🎉🏆</div>
        <h1 className="text-4xl font-bold text-yellow-700 dark:text-yellow-400">240K Lines!</h1>
        <p className="text-xl text-amber-600 mt-2">2,784 Commits · 8,228+ Files · 10 Modules</p>
        <p className="text-sm text-gray-500 mt-2">OpenSkill Developer Platform — Fully Operational</p>
        <div className="mt-4 inline-block px-6 py-2 bg-green-500 text-white rounded-full font-bold">
          ✅ ALL SYSTEMS GREEN
        </div>
      </div>
      <div className="grid grid-cols-6 gap-px bg-yellow-200 dark:bg-yellow-800">
        {stats.map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-xl">{s.icon}</div>
            <div className="text-lg font-bold text-yellow-700 dark:text-yellow-400">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
