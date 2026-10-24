"use client";

export function Milestone2700Banner() {
  return (
    <div className="rounded-xl border-2 border-yellow-500 overflow-hidden bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-900/10 dark:via-amber-900/10 dark:to-orange-900/10">
      <div className="p-8 text-center">
        <div className="text-5xl mb-3">🏆🎊🚀</div>
        <h2 className="text-3xl font-bold text-yellow-700 dark:text-yellow-400">2,700 Commits!</h2>
        <p className="text-lg text-amber-600 mt-1">233K+ Lines · 7,912+ Files</p>
        <p className="text-sm text-gray-500 mt-2">OpenSkill Developer Platform — All Systems Green</p>
        <div className="flex justify-center gap-4 mt-4">
          {[{ l: "Services", v: "1,350+" }, { l: "Components", v: "1,350+" }, { l: "Modules", v: "10" }].map(s => (
            <div key={s.l} className="px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-lg">
              <div className="text-sm font-bold text-yellow-700">{s.v}</div>
              <div className="text-[10px] text-gray-400">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
