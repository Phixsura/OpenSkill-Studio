"use client";

interface Stat { label: string; value: number; icon: string; }
interface PlatformStatsHeroProps { stats: Stat[]; title: string; subtitle: string; }

export function PlatformStatsHero({ stats, title, subtitle }: PlatformStatsHeroProps) {
  return (
    <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white">
      <h1 className="text-2xl font-bold">{title}</h1>
      <p className="mt-1 text-sm opacity-80">{subtitle}</p>
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map(s => (
          <div key={s.label} className="text-center">
            <span className="text-2xl">{s.icon}</span>
            <p className="mt-1 text-2xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-xs opacity-70">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
