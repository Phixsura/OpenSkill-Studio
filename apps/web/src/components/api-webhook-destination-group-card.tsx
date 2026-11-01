"use client";

interface GroupInfo { group_id: string; name: string; destination_count: number; enabled: boolean; }
interface Props { groups: GroupInfo[]; appName: string; }

export default function APIWebhookDestinationGroupCard({ groups, appName }: Props) {
  const active = groups.filter((g) => g.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📂 Destination Groups</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{groups.length} active</span>
      </div>
      {groups.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No destination groups</p>
      ) : (
        <div className="space-y-1">
          {groups.map((g) => (
            <div key={g.group_id} className={`flex items-center justify-between text-[11px] ${!g.enabled ? "opacity-50" : ""}`}>
              <span className="text-gray-700 dark:text-gray-300">{g.name}</span>
              <span className="text-gray-400">{g.destination_count} destinations</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
