"use client";

interface StepInfo { step_id: string; title: string; breaking: boolean; difficulty: string; }
interface GuideInfo { guide_id: string; from_version: string; to_version: string; steps: StepInfo[]; estimated_hours: number; breaking_count: number; }
interface Props { guides: GuideInfo[]; appName: string; }

const diffColor: Record<string, string> = { easy: "text-green-600 dark:text-green-400", medium: "text-yellow-600 dark:text-yellow-400", hard: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuideCard({ guides, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Migration Guides</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {guides.length} guides</p>
      </div>
      {guides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migration guides</p>
      ) : (
        <div className="space-y-2">
          {guides.map((g) => (
            <div key={g.guide_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700 dark:text-gray-300">{g.from_version} → {g.to_version}</span>
                <span className="text-gray-400">~{g.estimated_hours}h · {g.steps.length} steps</span>
              </div>
              {g.breaking_count > 0 && <span className="text-[10px] text-red-500">💥 {g.breaking_count} breaking</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
