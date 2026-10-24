"use client";

export function Milestone250K() {
  const stats = [
    { label: "Lines of Code", value: "250,000", icon: "📝" },
    { label: "Commits", value: "2,906+", icon: "📦" },
    { label: "Files", value: "8,640+", icon: "📁" },
    { label: "Services", value: "1,480+", icon: "⚙️" },
    { label: "Components", value: "1,480+", icon: "🧩" },
    { label: "Tests", value: "2,960+", icon: "✅" },
  ];
  const modules = [
    "Extension SDK", "Sandboxed Apps", "Marketplace", "Automation API",
    "Ecosystem", "Developer Portal", "Security", "Infrastructure",
    "Observability", "Platform Operations",
  ];
  return (
    <div className="rounded-2xl border-2 border-yellow-500 bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-950 dark:via-amber-950 dark:to-orange-950 overflow-hidden">
      <div className="p-8 text-center">
        <div className="text-5xl mb-3">🏆🏆🏆</div>
        <h1 className="text-3xl font-black tracking-tight mb-1">QUARTER MILLION</h1>
        <h2 className="text-xl font-bold text-amber-700 dark:text-amber-400 mb-1">250,000 Lines of Code</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">OpenSkill Developer Platform</p>
      </div>
      <div className="grid grid-cols-3 gap-3 px-6 pb-4">
        {stats.map(s => (
          <div key={s.label} className="bg-white/60 dark:bg-black/20 rounded-xl p-3 text-center">
            <div className="text-2xl mb-1">{s.icon}</div>
            <div className="font-black text-xl text-amber-700 dark:text-amber-400">{s.value}</div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">{s.label}</div>
          </div>
        ))}
      </div>
      <div className="bg-white/40 dark:bg-black/20 mx-6 mb-6 rounded-xl p-4">
        <div className="text-xs font-bold text-gray-500 uppercase mb-2">10 Platform Modules — All Operational ✅</div>
        <div className="flex flex-wrap gap-1.5">
          {modules.map(m => (
            <span key={m} className="text-[10px] px-2 py-0.5 rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">{m}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
