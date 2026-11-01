"use client";

interface ChangeInfo { change_type: string; target: string; description: string; }
interface DiffInfo { from_version: string; to_version: string; changes: ChangeInfo[]; breaking_count: number; additions: number; is_breaking: boolean; }
interface Props { diffs: DiffInfo[]; appName: string; }

const ctIcon: Record<string, string> = { added: "✨", removed: "🗑️", modified: "✏️", deprecated: "⚠️" };
const ctColor: Record<string, string> = { added: "text-green-600", removed: "text-red-600", modified: "text-yellow-600", deprecated: "text-orange-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiffCard({ diffs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Changelog Diff</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {diffs.length} diffs</p>
      </div>
      {diffs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No diffs</p>
      ) : (
        <div className="space-y-3">
          {diffs.map((d) => (
            <div key={`${d.from_version}-${d.to_version}`} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{d.from_version} → {d.to_version}</span>
                {d.is_breaking && <span className="rounded bg-red-100 px-1 py-0.5 text-[9px] text-red-700">breaking</span>}
              </div>
              <div className="mt-1 space-y-0.5">
                {d.changes.slice(0, 3).map((c, i) => (
                  <p key={i} className={`text-[10px] ${ctColor[c.change_type] ?? ""}`}>{ctIcon[c.change_type]} {c.target}</p>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
