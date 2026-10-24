"use client";
interface WarmupService { name: string; status: string; steps: number; }
interface WarmupCtrlPanelProps { services: WarmupService[]; warm: number; cold: number; }
export function WarmupCtrlPanel({ services, warm, cold }: WarmupCtrlPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Service Warmup</h3>
        <span className={`text-xs ${cold > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {warm} warm · {cold} cold
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${s.status === "warm" ? "bg-green-500" : "bg-blue-400"}`} />
              <span className="font-mono">{s.name}</span>
            </div>
            <span className="text-gray-400">{s.steps} steps · {s.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
