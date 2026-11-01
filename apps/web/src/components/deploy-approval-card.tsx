"use client";

interface DeployApprovalCardProps { deployId: string; version: string; env: string;
  status: string; approvals: number; required: number; rejectionReason?: string; }

const STATUS_STYLE: Record<string, string> = {
  pending: "text-yellow-600", approved: "text-green-600", rejected: "text-red-600",
};

export function DeployApprovalCard({ deployId, version, env, status, approvals, required, rejectionReason }: DeployApprovalCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Deploy Approval</h3>
        <span className={`text-xs font-bold uppercase ${STATUS_STYLE[status] ?? ""}`}>{status}</span>
      </div>
      <div className="p-4 space-y-2 text-xs">
        <div className="flex justify-between"><span className="text-gray-400">Deploy</span><span className="font-mono">{deployId}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Version</span><span>{version}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Environment</span><span className="uppercase">{env}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Approvals</span><span>{approvals}/{required}</span></div>
        {rejectionReason && <div className="text-red-500 mt-1">Reason: {rejectionReason}</div>}
      </div>
    </div>
  );
}
