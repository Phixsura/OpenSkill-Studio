"use client";
interface AvailabilityPanelProps { compositePct: number; downtimeMinutes: number; nines: number;
  components: number; architecture: string; }
export function AvailabilityPanel({ compositePct, downtimeMinutes, nines, components, architecture }: AvailabilityPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Availability</h3>
        <span className={`text-xs font-bold ${nines >= 3 ? "text-green-600" : nines >= 2 ? "text-yellow-600" : "text-red-500"}`}>
          {compositePct}% · {nines}-nines · {architecture}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Composite</span><div className="font-bold text-lg">{compositePct}%</div></div>
        <div><span className="text-gray-400">Downtime/mo</span><div className="font-bold text-lg">{downtimeMinutes}min</div></div>
        <div><span className="text-gray-400">Components</span><div className="font-bold text-lg">{components}</div></div>
      </div>
    </div>
  );
}
