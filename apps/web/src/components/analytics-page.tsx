"use client";

interface Kpi { label: string; display: string; icon: string; }
interface ChartPoint { date: string; count: number; }
interface Country { country: string; count: number; }
interface AnalyticsPageProps { appName: string; period: string; kpis: Kpi[];
  installChart: ChartPoint[]; topCountries: Country[]; }

export function AnalyticsPage({ appName, period, kpis, installChart, topCountries }: AnalyticsPageProps) {
  const maxInstall = Math.max(...installChart.map(p => p.count), 1);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 {appName} Analytics</h2>
        <span className="text-xs text-gray-400">{period}</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {kpis.map(k => (
          <div key={k.label} className="rounded-xl border p-4 text-center dark:border-gray-700">
            <span className="text-lg">{k.icon}</span>
            <p className="text-2xl font-bold mt-1">{k.display}</p>
            <p className="text-xs text-gray-400">{k.label}</p>
          </div>
        ))}
      </div>
      <div>
        <h3 className="text-sm font-semibold mb-2">Installs Over Time</h3>
        <div className="flex items-end gap-px h-24">
          {installChart.map((p, i) => (
            <div key={i} className="flex-1" title={`${p.date}: ${p.count}`}>
              <div className="w-full rounded-t bg-blue-500" style={{ height: `${(p.count / maxInstall) * 100}%`, minHeight: p.count > 0 ? 4 : 0 }} />
            </div>
          ))}
        </div>
      </div>
      {topCountries.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2">Top Countries</h3>
          {topCountries.map(c => (
            <div key={c.country} className="flex justify-between text-sm py-0.5">
              <span>{c.country}</span><span className="text-gray-400">{c.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
