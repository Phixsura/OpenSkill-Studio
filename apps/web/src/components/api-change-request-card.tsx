"use client";

interface ChangeRequestInfo {
  request_id: string;
  title: string;
  impact: string;
  status: "draft" | "pending" | "approved" | "rejected" | "implemented";
  submitter: string;
}

interface APIChangeRequestCardProps {
  requests: ChangeRequestInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  draft: "bg-gray-100 text-gray-500 dark:bg-gray-800",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  implemented: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
};

const impactStyle: Record<string, string> = {
  none: "text-gray-400", minor: "text-yellow-500", major: "text-orange-500", breaking: "text-red-500",
};

export default function APIChangeRequestCard({ requests, appName }: APIChangeRequestCardProps) {
  const pending = requests.filter((r) => r.status === "pending").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Change Requests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{requests.length} requests</span>
          {pending > 0 && <p className="text-[10px] text-yellow-600">{pending} pending</p>}
        </div>
      </div>

      {requests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No change requests</p>
      ) : (
        <div className="space-y-1.5">
          {requests.map((r) => (
            <div key={r.request_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[r.status]}`}>{r.status}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.title}</span>
              </div>
              <span className={`text-[10px] ${impactStyle[r.impact] ?? "text-gray-400"}`}>{r.impact}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
