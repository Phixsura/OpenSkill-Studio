"use client";

interface GroupInfo {
  group_id: string;
  name: string;
  member_count: number;
  rate_limit: number;
}

interface APIConsumerGroupCardProps {
  groups: GroupInfo[];
  appName: string;
}

export default function APIConsumerGroupCard({ groups, appName }: APIConsumerGroupCardProps) {
  const totalMembers = groups.reduce((s, g) => s + g.member_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Consumer Groups</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{groups.length} groups · {totalMembers} members</span>
      </div>

      {groups.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumer groups</p>
      ) : (
        <div className="space-y-1.5">
          {groups.map((g) => (
            <div key={g.group_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{g.name}</span>
              <div className="text-[10px] text-gray-400">
                {g.member_count} members{g.rate_limit > 0 ? ` · ${g.rate_limit}/min` : ""}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
