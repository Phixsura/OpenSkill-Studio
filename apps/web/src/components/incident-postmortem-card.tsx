"use client";

interface ActionItemInfo {
  description: string;
  owner: string;
  completed: boolean;
}

interface PostmortemInfo {
  postmortem_id: string;
  title: string;
  root_cause: string;
  impact: string;
  action_items: ActionItemInfo[];
  completion_pct: number;
}

interface IncidentPostmortemCardProps {
  postmortem: PostmortemInfo;
  appName: string;
}

export default function IncidentPostmortemCard({
  postmortem: pm,
  appName,
}: IncidentPostmortemCardProps) {
  const completed = pm.action_items.filter((a) => a.completed).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{pm.title}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · Postmortem</p>
        </div>
        <span
          className={`text-xs font-medium ${pm.completion_pct >= 100 ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"}`}
        >
          {pm.completion_pct}% complete
        </span>
      </div>

      <div className="mb-3 space-y-1.5">
        <div>
          <p className="text-[10px] font-medium text-gray-500">Root Cause</p>
          <p className="text-xs text-gray-700 dark:text-gray-300">{pm.root_cause}</p>
        </div>
        <div>
          <p className="text-[10px] font-medium text-gray-500">Impact</p>
          <p className="text-xs text-gray-700 dark:text-gray-300">{pm.impact}</p>
        </div>
      </div>

      {pm.action_items.length > 0 && (
        <div>
          <p className="mb-1 text-[10px] font-medium text-gray-500">
            Actions ({completed}/{pm.action_items.length})
          </p>
          <div className="space-y-1">
            {pm.action_items.map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className={a.completed ? "text-green-500" : "text-gray-300"}>
                  {a.completed ? "✓" : "○"}
                </span>
                <span
                  className={
                    a.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"
                  }
                >
                  {a.description}
                </span>
                <span className="text-[10px] text-gray-400">({a.owner})</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
