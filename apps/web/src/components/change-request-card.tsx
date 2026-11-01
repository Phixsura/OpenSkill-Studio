"use client";

interface ChangeRequestCardProps { crId: string; title: string; description: string;
  risk: string; requester: string; currentApprovals: number; minApprovals: number;
  status: string; onApprove: () => void; onReject: () => void; }

const riskBadge: Record<string, string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-900/30",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function ChangeRequestCard({ crId, title, description, risk, requester,
  currentApprovals, minApprovals, status, onApprove, onReject }: ChangeRequestCardProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-gray-400">{crId}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs ${riskBadge[risk] ?? ""}`}>{risk}</span>
          </div>
          <h3 className="mt-1 font-semibold">{title}</h3>
          <p className="text-xs text-gray-400">{description}</p>
          <p className="mt-1 text-xs text-gray-300">by {requester}</p>
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-xs ${status === "approved" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {status}
        </span>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-gray-400">Approvals: {currentApprovals}/{minApprovals}</span>
        {status === "pending" && (
          <div className="flex gap-2">
            <button onClick={onApprove} className="rounded bg-green-600 px-3 py-1 text-xs text-white">Approve</button>
            <button onClick={onReject} className="rounded border border-red-300 px-3 py-1 text-xs text-red-600">Reject</button>
          </div>
        )}
      </div>
    </div>
  );
}
