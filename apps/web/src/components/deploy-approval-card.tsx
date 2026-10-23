"use client";

interface Approval { approver: string; comment: string; }
interface DeployApprovalCardProps { deployId: string; version: string; env: string;
  requester: string; status: string; approvals: Approval[];
  required: number; onApprove: () => void; onReject: () => void; }

const STATUS_STYLE: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700", approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export function DeployApprovalCard({ deployId, version, env, requester, status,
  approvals, required, onApprove, onReject }: DeployApprovalCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🚦 Deploy Approval</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_STYLE[status] || ""}`}>{status}</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-sm mb-4">
        <div><p className="font-mono font-bold">{version}</p><p className="text-xs text-gray-400">Version</p></div>
        <div><p className="font-bold capitalize">{env}</p><p className="text-xs text-gray-400">Environment</p></div>
        <div><p className="font-bold">{approvals.length}/{required}</p><p className="text-xs text-gray-400">Approvals</p></div>
      </div>
      {approvals.length > 0 && (
        <div className="space-y-1 mb-3">
          {approvals.map(a => (
            <div key={a.approver} className="flex items-center gap-2 text-xs">
              <span className="text-green-500">✅</span>
              <span className="font-medium">{a.approver}</span>
              {a.comment && <span className="text-gray-400">— {a.comment}</span>}
            </div>
          ))}
        </div>
      )}
      {status === "pending" && (
        <div className="flex gap-2">
          <button onClick={onApprove} className="flex-1 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700">Approve</button>
          <button onClick={onReject} className="flex-1 py-2 border border-red-200 text-red-600 text-sm rounded hover:bg-red-50">Reject</button>
        </div>
      )}
    </div>
  );
}
