"use client";

interface PlatformProgressBarProps { commits: number; lines: number; files: number;
  services: number; components: number; target: string; }

export function PlatformProgressBar({ commits, lines, files, services, components, target }: PlatformProgressBarProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Platform Progress</h2>
        <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30">
          Target: {target}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-5 gap-3 text-center">
        {[
          { label: "Commits", value: commits, icon: "📝" },
          { label: "Lines", value: lines, icon: "📏" },
          { label: "Files", value: files, icon: "📁" },
          { label: "Services", value: services, icon: "⚙️" },
          { label: "Components", value: components, icon: "🧩" },
        ].map(s => (
          <div key={s.label}>
            <span className="text-lg">{s.icon}</span>
            <p className="text-lg font-bold">{s.value.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
