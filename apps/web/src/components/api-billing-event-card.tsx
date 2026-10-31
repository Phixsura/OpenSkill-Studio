"use client";

interface BillingByType {
  event_type: string;
  amount: number;
}

interface APIBillingEventCardProps {
  byType: BillingByType[];
  total: number;
  currency: string;
  eventCount: number;
  appName: string;
}

export default function APIBillingEventCard({ byType, total, currency, eventCount, appName }: APIBillingEventCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💵 Billing Events</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{currency} {total.toFixed(2)}</span>
          <p className="text-[10px] text-gray-400">{eventCount} events</p>
        </div>
      </div>

      {byType.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No billing events</p>
      ) : (
        <div className="space-y-1">
          {byType.map((b) => (
            <div key={b.event_type} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.event_type}</span>
              <span className="font-mono text-gray-400">{currency} {b.amount.toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
