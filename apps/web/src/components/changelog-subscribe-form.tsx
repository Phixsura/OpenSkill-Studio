"use client";
import { useState } from "react";

interface ChangelogSubscribeFormProps { onSubscribe: (email: string, freq: string) => void;
  subscriberCount: number; }

export function ChangelogSubscribeForm({ onSubscribe, subscriberCount }: ChangelogSubscribeFormProps) {
  const [email, setEmail] = useState("");
  const [freq, setFreq] = useState("weekly");
  const handleSubmit = () => { if (email.includes("@")) { onSubscribe(email, freq); setEmail(""); } };
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-md">
      <h3 className="font-semibold mb-1">📬 Stay Updated</h3>
      <p className="text-xs text-gray-400 mb-3">Join {subscriberCount.toLocaleString()} subscribers</p>
      <div className="flex gap-2 mb-2">
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com"
          className="flex-1 text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <select value={freq} onChange={e => setFreq(e.target.value)}
          className="text-sm px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600">
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <button onClick={handleSubmit}
        className="w-full py-2 bg-blue-600 text-white text-sm rounded font-medium hover:bg-blue-700">Subscribe</button>
    </div>
  );
}
