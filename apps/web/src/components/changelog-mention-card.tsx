"use client";

interface MentionInfo {
  version: string;
  users: string[];
  issues: number[];
  prs: number[];
}

interface ChangelogMentionCardProps {
  mentions: MentionInfo[];
  appName: string;
}

export default function ChangelogMentionCard({ mentions, appName }: ChangelogMentionCardProps) {
  const allUsers = [...new Set(mentions.flatMap((m) => m.users))].sort();
  const totalIssues = new Set(mentions.flatMap((m) => m.issues)).size;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Mentions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{allUsers.length} contributors</span>
          <span>· {totalIssues} issues</span>
        </div>
      </div>

      {mentions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mentions found</p>
      ) : (
        <div className="space-y-2.5">
          {mentions.map((m) => (
            <div
              key={m.version}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">
                v{m.version}
              </span>
              <div className="mt-1.5 flex flex-wrap gap-1">
                {m.users.map((u) => (
                  <span
                    key={u}
                    className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                  >
                    @{u}
                  </span>
                ))}
                {m.issues.map((i) => (
                  <span
                    key={`i${i}`}
                    className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700 dark:bg-green-900/30 dark:text-green-400"
                  >
                    #{i}
                  </span>
                ))}
                {m.prs.map((p) => (
                  <span
                    key={`p${p}`}
                    className="rounded-full bg-purple-100 px-2 py-0.5 text-[10px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
                  >
                    PR #{p}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
