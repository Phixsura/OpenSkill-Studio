"use client";
export function FleetAiModelBillV2Panel({ billers, active, models, revenue, invoices }: { billers: number; active: number; models: number; revenue: number; invoices: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💳 AI Model Billing v2</h3>
    <div className="text-sm">{active}/{billers} active · {models} models · ${revenue.toLocaleString()} · {invoices.toLocaleString()} invoices</div>
  </div>);
}
