"use client";
export function FleetBedrockPanel({ models, available, invocations, tokens }: { models: number; available: number; invocations: number; tokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪨 Bedrock</h3>
    <div className="text-sm">{available}/{models} available · {invocations.toLocaleString()} inv · {tokens.toLocaleString()} tokens</div>
  </div>);
}
