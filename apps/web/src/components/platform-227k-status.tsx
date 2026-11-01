"use client";

export function Platform227kStatus() {
  const stats = [
    { label: "Commits", value: "2,640+", icon: "📝" },
    { label: "Lines", value: "227K+", icon: "📊" },
    { label: "Files", value: "7,680+", icon: "📁" },
    { label: "Services", value: "1,320+", icon: "⚙️" },
    { label: "Components", value: "1,320+", icon: "🧩" },
    { label: "Modules", value: "10", icon: "📦" },
  ];
  return (
    <div className="rounded-xl border-2 border-indigo-500 overflow-hidden bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/10 dark:to-purple-900/10">
      <div className="p-6 text-center">
        <div className="text-3xl mb-1">🚀</div>
        <h2 className="text-xl font-bold text-indigo-700 dark:text-indigo-400">227K+ Lines · All Systems Go</h2>
      </div>
      <div className="grid grid-cols-6 gap-px bg-indigo-200 dark:bg-indigo-800">
        {stats.map(s => (
          <div key={s.label} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm">{s.icon}</div>
            <div className="text-sm font-bold text-indigo-700 dark:text-indigo-400">{s.value}</div>
            <div className="text-[9px] text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
