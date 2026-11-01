"use client";

interface SDKEntry { version: string; changes: string[]; breaking: boolean; }
interface Props { entries: SDKEntry[]; appName: string; }

export default function APISDKChangelogCard({ entries, appName }: Props) {
  const breaking = entries.filter((e) => e.breaking).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 SDK Changelog</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{entries.length} versions</span>
          {breaking > 0 && <p className="text-[10px] text-red-500">{breaking} breaking</p>}
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK versions</p>
      ) : (
        <div className="space-y-2">
          {entries.slice(0, 5).map((e) => (
            <div key={e.version} className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">{e.version}</span>
                {e.breaking && <span className="text-[9px] text-red-500">breaking</span>}
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{e.changes.length} changes</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
