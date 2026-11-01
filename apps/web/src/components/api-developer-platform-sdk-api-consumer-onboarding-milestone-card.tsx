"use client";

interface MilestoneInfo { consumer_id: string; completed_count: number; completion_pct: number; next_milestone: string | null; fully_onboarded: boolean; }
interface Props { consumers: MilestoneInfo[]; completionRate: number; fullyOnboardedCount: number; appName: string; }

const MILESTONES = ["registered", "api_key_created", "first_api_call", "first_webhook", "production_traffic", "first_payment"];

export default function APIDeveloperPlatformSDKApiConsumerOnboardingMilestoneCard({ consumers, completionRate, fullyOnboardedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Onboarding Milestones</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-bold text-green-600">{fullyOnboardedCount} complete</span>
          <p className="text-[9px] text-gray-400">{completionRate}% rate</p>
        </div>
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No milestone data</p>
      ) : (
        <div className="space-y-1.5">
          {consumers.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <div className="flex items-center gap-1.5">
                <span className="text-gray-400">{c.completed_count}/{MILESTONES.length}</span>
                {c.fully_onboarded ? <span className="text-green-500">✓</span> : <span className="text-[9px] text-blue-500">→ {c.next_milestone?.replace(/_/g, " ")}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
