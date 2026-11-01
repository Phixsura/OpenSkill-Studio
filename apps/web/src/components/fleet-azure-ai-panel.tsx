"use client";
export function FleetAzureAiPanel({ services, active, calls, models }: { services: number; active: number; calls: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Azure AI</h3>
    <div className="text-sm">{active}/{services} active · {calls.toLocaleString()} calls · {models} models</div>
  </div>);
}
