"use client";
interface RegistryFinalPanelProps { totalServices: number; modules: number; active: number;
  allActive: boolean; byModule: Record<string, number>; }
export function RegistryFinalPanel({ totalServices, modules, active, allActive, byModule }: RegistryFinalPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Service Registry</h3>
        <span className={`text-xs font-bold ${allActive ? "text-green-600" : "text-yellow-600"}`}>
          {totalServices} services · {modules} modules · {active} active
        </span>
      </div>
      <div className="p-4 flex flex-wrap gap-1.5">
        {Object.entries(byModule).map(([mod, count]) => (
          <span key={mod} className="text-[10px] px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
            {mod}: {count}
          </span>
        ))}
      </div>
    </div>
  );
}
