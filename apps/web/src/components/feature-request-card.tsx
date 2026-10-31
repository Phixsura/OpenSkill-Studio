"use client";

interface FeatureRequestInfo {
  request_id: string;
  title: string;
  status: "open" | "planned" | "in_progress" | "done" | "declined";
  vote_count: number;
  tags: string[];
}

interface FeatureRequestCardProps {
  requests: FeatureRequestInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  open: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  planned: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  done: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  declined: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

export default function FeatureRequestCard({ requests, appName }: FeatureRequestCardProps) {
  const open = requests.filter((r) => r.status === "open").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            💡 Feature Requests
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {open} open / {requests.length} total
        </span>
      </div>

      {requests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature requests</p>
      ) : (
        <div className="space-y-1.5">
          {requests.map((r) => (
            <div
              key={r.request_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
                  {r.vote_count}
                </span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.title}</span>
              </div>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[r.status]}`}
              >
                {r.status.replace("_", " ")}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
