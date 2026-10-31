"use client";

interface Metric { label: string; value: number | string; display: string; }
interface SummaryCardProps { title: string; icon: string; metrics: Metric[];
  status: string; link: string | null; onClick?: () => void; }

const statusDot: Record<string, string> = { ok: "bg-green-500", warning: "bg-yellow-500", error: "bg-red-500" };

export function SummaryCard({ title, icon, metrics, status, link, onClick }: SummaryCardProps) {
  return (
    <div className="rounded-xl border p-4 hover:shadow dark:border-gray-700" onClick={onClick}
      role={onClick ? "button" : undefined}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <h3 className="font-semibold">{title}</h3>
        </div>
        <span className={`h-2 w-2 rounded-full ${statusDot[status] ?? statusDot.ok}`} />
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        {metrics.map(m => (
          <div key={m.label} className="text-center">
            <p className="text-lg font-bold">{m.display}</p>
            <p className="text-[10px] text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
