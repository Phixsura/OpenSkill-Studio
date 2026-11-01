"use client";

interface SegmentInfo { segment_id: string; name: string; member_count: number; criteria: Record<string, string>; }
interface Props { segments: SegmentInfo[]; appName: string; }

export default function APIDeveloperAPIApiConsumerSegmentationCard({ segments, appName }: Props) {
  const totalMembers = segments.reduce((s, seg) => s + seg.member_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Consumer Segments</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {segments.length} segments · {totalMembers} members</p>
      </div>
      {segments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No segments</p>
      ) : (
        <div className="space-y-2">
          {segments.map((s) => (
            <div key={s.segment_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{s.name}</span>
                {Object.keys(s.criteria).length > 0 && (
                  <p className="text-[9px] text-gray-400">{Object.entries(s.criteria).map(([k, v]) => `${k}=${v}`).join(", ")}</p>
                )}
              </div>
              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">{s.member_count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
