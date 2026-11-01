"use client";
export function FleetIdpFederationV9Panel({ providers, connected }: { providers: number; connected: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪪 IdP Federation v9</h3>
    <div className="text-sm">{providers} providers · {connected} connected</div>
  </div>);
}
