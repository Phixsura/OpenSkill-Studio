"use client";

export function Milestone230kBanner() {
  const stats = [
    { l: "Commits", v: "2,666+", icon: "📝" },
    { l: "Lines", v: "230K+", icon: "📊" },
    { l: "Files", v: "7,784+", icon: "📁" },
    { l: "Services", v: "1,333+", icon: "⚙️" },
    { l: "Components", v: "1,333+", icon: "🧩" },
    { l: "Modules", v: "10", icon: "📦" },
  ];
  return (
    <div className="rounded-xl border-2 border-yellow-500 overflow-hidden bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/10 dark:to-amber-900/10">
      <div className="p-6 text-center">
        <div className="text-4xl mb-2">🏆🎊🏆</div>
        <h2 className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">230K Lines!</h2>
        <p className="text-sm text-gray-400 mt-1">OpenSkill Developer Platform — Fully Operational</p>
      </div>
      <div className="grid grid-cols-6 gap-px bg-yellow-200 dark:bg-yellow-800">
        {stats.map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm">{s.icon}</div>
            <div className="text-sm font-bold text-yellow-700 dark:text-yellow-400">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
