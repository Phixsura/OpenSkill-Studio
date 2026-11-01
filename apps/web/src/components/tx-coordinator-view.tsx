"use client";

interface Transaction { txId: string; participants: string[]; status: string;
  votesReceived: number; }
interface TxCoordinatorViewProps { transactions: Transaction[];
  committed: number; aborted: number; successRate: number; }

const STATUS_COLORS: Record<string, string> = {
  committed: "bg-green-100 text-green-700", aborted: "bg-red-100 text-red-700",
  preparing: "bg-blue-100 text-blue-700",
};

export function TxCoordinatorView({ transactions, committed, aborted, successRate }: TxCoordinatorViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Transactions</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{committed} committed</span>
          {aborted > 0 && <span className="text-red-500">{aborted} aborted</span>}
          <span className="text-gray-400">{successRate}%</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {transactions.map(tx => (
          <div key={tx.txId} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-xs font-mono">{tx.txId}</span>
              <div className="text-[10px] text-gray-400">{tx.participants.join(", ")} · {tx.votesReceived} votes</div>
            </div>
            <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[tx.status] ?? ""}`}>{tx.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
