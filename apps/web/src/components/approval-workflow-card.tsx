"use client";

interface ApprovalWorkflowCardProps {
  type: string; description: string; status: string; requester: string;
  onApprove: () => void; onReject: () => void;
}

const STATUS_STYLES: Record<string, { color: string; icon: string }> = {
  pending: { color: "text-yellow-600", icon: "⏳" },
  approved: { color: "text-green-600", icon: "✅" },
  rejected: { color: "text-red-600", icon: "❌" },
};

export function ApprovalWorkflowCard({ type, description, status, requester, onApprove, onReject }: ApprovalWorkflowCardProps) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.pending;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{type}</span>
          <h3 className="mt-1 font-semibold">{description}</h3>
          <p className="text-xs text-gray-400">Requested by {requester}</p>
        </div>
        <span className={style.color}>{style.icon} {status}</span>
      </div>
      {status === "pending" && (
        <div className="mt-3 flex justify-end gap-2">
          <button onClick={onReject} className="rounded border px-3 py-1 text-xs text-red-600">Reject</button>
          <button onClick={onApprove} className="rounded bg-green-600 px-3 py-1 text-xs text-white">Approve</button>
        </div>
      )}
    </div>
  );
}
