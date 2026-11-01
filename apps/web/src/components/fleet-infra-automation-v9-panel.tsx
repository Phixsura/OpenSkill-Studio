"use client";
export function FleetInfraAutomationV9Panel({ resources, coverage }: { resources: number; coverage: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Infra Automation v9</h3>
    <div className="text-sm">{resources} resources · {coverage}% IaC</div>
  </div>);
}
