"use client";

interface HealthInfo { api_health: number; webhook_health: number; documentation_health: number; developer_experience: number; overall: number; grade: string; }
interface Props { health: HealthInfo; appName: string; }

const gColor: Record<string, string> = { "A+": "text-green-600", A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperPlatformHealthCard({ health: h, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌟 Platform Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-3xl font-bold ${gColor[h.grade] ?? "text-gray-500"}`}>{h.grade}</span>
          <p className="text-[10px] text-gray-400">{h.overall}%</p>
        </div>
      </div>
      <div className="space-y-1.5">
        {[
          { l: "API", v: h.api_health },
          { l: "Webhooks", v: h.webhook_health },
          { l: "Documentation", v: h.documentation_health },
          { l: "Dev Experience", v: h.developer_experience },
        ].map((m) => (
          <div key={m.l}>
            <div className="flex justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{m.l}</span>
              <span className="text-gray-400">{m.v}%</span>
            </div>
            <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
              <div className={`h-1 rounded-full ${m.v >= 90 ? "bg-green-500" : m.v >= 70 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${m.v}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
