"use client";

interface ChannelInfo { color: string; icon: string; label: string; }
interface VersionBadgeProps { display: string; channelInfo: ChannelInfo; isLatest: boolean; }

const colorMap: Record<string, string> = {
  green: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  yellow: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  orange: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  blue: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
};

export function VersionBadge({ display, channelInfo, isLatest }: VersionBadgeProps) {
  return (
    <div className="inline-flex items-center gap-1.5">
      <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colorMap[channelInfo.color] ?? colorMap.green}`}>
        {channelInfo.icon} {display}
      </span>
      {isLatest && <span className="text-[10px] text-green-500">Latest</span>}
    </div>
  );
}
