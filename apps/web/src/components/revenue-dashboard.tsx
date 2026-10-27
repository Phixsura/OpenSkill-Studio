"use client";

interface Earnings { totalGross: number; totalNet: number; totalFees: number; transactionCount: number; }

function formatCents(cents: number) { return `$${(cents / 100).toFixed(2)}`; }

export function RevenueDashboard({ earnings }: { earnings: Earnings }) {
  return (
    <div className="space-y-4">
      <h3 className="font-bold text-sm">Revenue Overview</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="border dark:border-gray-700 rounded-xl p-3 text-center">
          <span className="text-2xl font-bold text-green-600 block">{formatCents(earnings.totalNet)}</span>
          <span className="text-xs text-gray-500">Net Earnings</span>
        </div>
        <div className="border dark:border-gray-700 rounded-xl p-3 text-center">
          <span className="text-2xl font-bold block">{formatCents(earnings.totalGross)}</span>
          <span className="text-xs text-gray-500">Gross Revenue</span>
        </div>
        <div className="border dark:border-gray-700 rounded-xl p-3 text-center">
          <span className="text-2xl font-bold text-orange-500 block">{formatCents(earnings.totalFees)}</span>
          <span className="text-xs text-gray-500">Platform Fees</span>
        </div>
        <div className="border dark:border-gray-700 rounded-xl p-3 text-center">
          <span className="text-2xl font-bold text-blue-500 block">{earnings.transactionCount}</span>
          <span className="text-xs text-gray-500">Transactions</span>
        </div>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden flex">
        <div className="h-full bg-green-500" style={{ width: `${earnings.totalGross > 0 ? (earnings.totalNet / earnings.totalGross * 100) : 0}%` }} />
        <div className="h-full bg-orange-400" style={{ width: `${earnings.totalGross > 0 ? (earnings.totalFees / earnings.totalGross * 100) : 0}%` }} />
      </div>
      <div className="flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Your share</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-400" /> Platform fee</span>
      </div>
    </div>
  );
}
