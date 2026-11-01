"use client";

interface Region { id: string; name: string; flag: string; continent: string; latency_ms: number; }
interface GeoRegionSelectorProps { regions: Region[]; selected: string; recommended: string;
  onSelect: (id: string) => void; }

export function GeoRegionSelector({ regions, selected, recommended, onSelect }: GeoRegionSelectorProps) {
  const grouped = regions.reduce<Record<string, Region[]>>((acc, r) => {
    (acc[r.continent] ??= []).push(r); return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Select Region</h3>
      {Object.entries(grouped).map(([continent, regs]) => (
        <div key={continent}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-2">{continent}</p>
          <div className="space-y-1">
            {regs.map(r => (
              <button key={r.id} onClick={() => onSelect(r.id)}
                className={`flex w-full items-center justify-between rounded-lg border px-4 py-2.5 text-sm ${selected === r.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
                <div className="flex items-center gap-2">
                  <span>{r.flag}</span>
                  <span className="font-medium">{r.name}</span>
                  {r.id === recommended && <span className="rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">Recommended</span>}
                </div>
                <span className="text-xs text-gray-400">{r.latency_ms}ms</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
