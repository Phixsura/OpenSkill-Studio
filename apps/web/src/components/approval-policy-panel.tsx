"use client";
interface ApprovalPolicyPanelProps { requiresApproval: boolean; requiredApprovers: string[];
  matchedPolicies: string[]; autoApprove: boolean; }
export function ApprovalPolicyPanel({ requiresApproval, requiredApprovers, matchedPolicies, autoApprove }: ApprovalPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Approval Policy</h3>
        <span className={`text-xs font-bold ${autoApprove ? "text-green-600" : "text-yellow-600"}`}>
          {autoApprove ? "✅ Auto-approved" : `⚠ ${requiredApprovers.length} approvers needed`}
        </span>
      </div>
      {!autoApprove && (
        <div className="p-4 text-xs space-y-1">
          <div className="text-gray-400">Approvers: {requiredApprovers.join(", ")}</div>
          <div className="text-gray-400">Policies: {matchedPolicies.join(", ")}</div>
        </div>
      )}
    </div>
  );
}
