"use client";

interface ProfileInfo { developer_id: string; display_name: string; email: string; bio: string; app_count: number; api_key_count: number; }
interface Props { profiles: ProfileInfo[]; appName: string; }

export default function APIDeveloperProfileCard({ profiles, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👩‍💻 Developer Profiles</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{profiles.length} developers</span>
      </div>
      {profiles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No developer profiles</p>
      ) : (
        <div className="space-y-2">
          {profiles.map((p) => (
            <div key={p.developer_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{p.display_name}</span>
                <span className="text-[10px] text-gray-400">{p.app_count} apps · {p.api_key_count} keys</span>
              </div>
              <p className="text-[10px] text-gray-400">{p.email}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
