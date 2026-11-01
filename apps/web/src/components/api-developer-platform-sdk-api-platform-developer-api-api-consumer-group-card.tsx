"use client";

interface GroupInfo { group_id: string; name: string; member_count: number; max_members: number; policy_count: number; }
interface Props { groups: GroupInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroupCard({ groups, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Consumer Groups</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {groups.length} groups</p>
      </div>
      {groups.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumer groups</p>
      ) : (
        <div className="space-y-1.5">
          {groups.map((g) => (
            <div key={g.group_id} className="flex items-center justify-between text-[11px]">
              <span className="font-medium text-gray-700 dark:text-gray-300">{g.name}</span>
              <span className="text-gray-400">{g.member_count}/{g.max_members} members · {g.policy_count} policies</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
