"use client";

interface Approval { approver: string; }
interface DeployApprovalCardProps { deployId: string; environment: string;
  requester: string; requiredApprovers: string[]; approvals: Approval[];
  status: string; onApprove: () => void; onReject: () => void; }

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700", approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export function DeployApprovalCard({ deployId, environment, requester, requiredApprovers, approvals, status, onApprove, onReject }: DeployApprovalCardProps) {
  const approvedBy = new Set(approvals.map(a => a.approver));
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🔐 Deploy Approval</h3>
          <div className="text-[10px] text-gray-400">{deployId} · {environment} · by {requester}</div>
        </div>
        <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[status] ?? ""}`}>{status}</span>
      </div>
      <div className="p-4">
        <div className="text-xs text-gray-400 mb-2">Required Approvers</div>
        <div className="flex gap-2 flex-wrap">
          {requiredApprovers.map(a => (
            <span key={a} className={`px-2 py-0.5 text-xs rounded ${approvedBy.has(a) ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
              {approvedBy.has(a) ? "✓" : "○"} {a}
            </span>
          ))}
        </div>
      </div>
      {status === "pending" && (
        <div className="flex gap-2 p-3 border-t dark:border-gray-700">
          <button onClick={onApprove} className="flex-1 py-1.5 text-xs bg-green-500 text-white rounded-lg">✓ Approve</button>
          <button onClick={onReject} className="flex-1 py-1.5 text-xs bg-red-500 text-white rounded-lg">✗ Reject</button>
        </div>
      )}
    </div>
  );
}
