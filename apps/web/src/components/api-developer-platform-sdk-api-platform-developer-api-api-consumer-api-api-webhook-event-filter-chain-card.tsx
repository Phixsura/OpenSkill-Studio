"use client";

interface StepInfo { step_id: string; filter_type: string; inverted: boolean; }
interface ChainInfo { chain_id: string; mode: string; steps: StepInfo[]; }
interface Props { chains: ChainInfo[]; appName: string; }

const filterIcon: Record<string, string> = { event_type: "📧", field_match: "🔍", payload_size: "📏", consumer: "👤" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChainCard({ chains, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Filter Chains</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {chains.length} chains</p>
      </div>
      {chains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No filter chains</p>
      ) : (
        <div className="space-y-2">
          {chains.map((c) => (
            <div key={c.chain_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.chain_id}</span>
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{c.mode}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {c.steps.map((s) => <span key={s.step_id} className={`rounded px-1 text-[9px] ${s.inverted ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>{filterIcon[s.filter_type] ?? "•"} {s.filter_type}{s.inverted ? " ✗" : ""}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
