"use client";
export function FleetTwilioPanel({ accounts, active, messages, calls }: { accounts: number; active: number; messages: number; calls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📱 Twilio</h3>
    <div className="text-sm">{active}/{accounts} active · {messages.toLocaleString()} msgs · {calls.toLocaleString()} calls</div>
  </div>);
}
