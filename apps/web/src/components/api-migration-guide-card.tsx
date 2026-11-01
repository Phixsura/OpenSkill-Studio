"use client";

interface GuideInfo {
  guide_id: string;
  from_version: string;
  to_version: string;
  step_count: number;
  breaking_count: number;
  completed_count: number;
}

interface APIMigrationGuideCardProps {
  guides: GuideInfo[];
  appName: string;
}

export default function APIMigrationGuideCard({ guides, appName }: APIMigrationGuideCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Migration Guides</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{guides.length} guides</span>
      </div>

      {guides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migration guides</p>
      ) : (
        <div className="space-y-2">
          {guides.map((g) => (
            <div key={g.guide_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{g.from_version} → {g.to_version}</span>
                <span className="text-[10px] text-gray-400">{g.completed_count} migrated</span>
              </div>
              <div className="mt-0.5 flex gap-2 text-[10px] text-gray-400">
                <span>{g.step_count} steps</span>
                {g.breaking_count > 0 && <span className="text-red-500">{g.breaking_count} breaking</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
