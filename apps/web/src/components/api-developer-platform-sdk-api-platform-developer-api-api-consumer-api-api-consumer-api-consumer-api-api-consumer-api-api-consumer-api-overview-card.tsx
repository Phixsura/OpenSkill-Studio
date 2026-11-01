"use client";

interface Metric { name: string; value: number; unit: string; trend: string; changePct: number; }
interface Props { consumerId: string; plan: string; status: string; healthScore: number; activeKeys: number; activeWebhooks: number; teamMembers: number; metrics: Metric[]; onboardingComplete: boolean; appName: string; }

const trendIcons: Record<string, string> = { up: "📈", down: "📉", stable: "➡️" };
const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  suspended: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  trial: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverviewCard({ consumerId, plan, status, healthScore, activeKeys, activeWebhooks, teamMembers, metrics, onboardingComplete, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏠 Consumer Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {plan}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${statusColors[status] ?? ""}`}>{status}</span>
      </div>
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${healthScore >= 80 ? "text-green-600" : healthScore >= 50 ? "text-amber-600" : "text-red-600"}`}>{healthScore}</div><div className="text-[9px] text-gray-400">Health</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{activeKeys}</div><div className="text-[9px] text-gray-400">Keys</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{activeWebhooks}</div><div className="text-[9px] text-gray-400">Webhooks</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{teamMembers}</div><div className="text-[9px] text-gray-400">Team</div></div>
      </div>
      {metrics.length > 0 && (
        <div className="space-y-0.5">
          {metrics.map((m) => (
            <div key={m.name} className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500">{m.name}</span>
              <span className="text-gray-700 dark:text-gray-300">{m.value.toLocaleString()} {m.unit} {trendIcons[m.trend]}</span>
            </div>
          ))}
        </div>
      )}
      {!onboardingComplete && <div className="mt-2 rounded bg-amber-50 p-1 text-center text-[10px] text-amber-700 dark:bg-amber-900/20 dark:text-amber-400">⚠ Onboarding incomplete</div>}
    </div>
  );
}
