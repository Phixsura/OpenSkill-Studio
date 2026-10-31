"use client";

interface TimelineEntry { status: string; icon: string; message: string; timestamp: string; }
interface IncidentPageProps { title: string; severity: string; status: string;
  statusIcon: string; affectedServices: string[]; timeline: TimelineEntry[];
  isResolved: boolean; createdAt: string; }

const sevColors: Record<string, string> = {
  minor: "bg-yellow-100 text-yellow-700", major: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

export function IncidentPage({ title, severity, status, statusIcon, affectedServices,
  timeline, isResolved, createdAt }: IncidentPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xl">{statusIcon}</span>
          <h1 className="text-xl font-bold">{title}</h1>
        </div>
        <div className="flex items-center gap-2">
          <span className={`rounded px-2 py-0.5 text-xs ${sevColors[severity] ?? ""} dark:bg-opacity-30`}>{severity}</span>
          <span className="text-xs text-gray-400 capitalize">{status}</span>
          {isResolved && <span className="text-xs text-green-600">✅ Resolved</span>}
        </div>
      </div>
      {affectedServices.length > 0 && (
        <div className="flex gap-1.5">
          <span className="text-xs text-gray-400">Affected:</span>
          {affectedServices.map(s => (
            <span key={s} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{s}</span>
          ))}
        </div>
      )}
      <div className="relative space-y-4 pl-6 border-l-2 border-gray-200 dark:border-gray-700">
        {timeline.map((t, i) => (
          <div key={i} className="relative">
            <span className="absolute -left-[25px] text-sm">{t.icon}</span>
            <p className="text-sm font-medium capitalize">{t.status}</p>
            <p className="text-sm text-gray-500">{t.message}</p>
            <time className="text-xs text-gray-400">{new Date(t.timestamp).toLocaleString()}</time>
          </div>
        ))}
      </div>
    </div>
  );
}
