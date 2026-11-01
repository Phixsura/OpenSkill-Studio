"use client";
import { useState } from "react";

interface ApiChangelogSubscribeProps { versions: string[];
  onSubscribe: (email: string, prefs: Record<string, boolean>) => void; }

export function ApiChangelogSubscribe({ versions, onSubscribe }: ApiChangelogSubscribeProps) {
  const [email, setEmail] = useState("");
  const [breaking, setBreaking] = useState(true);
  const [deprecations, setDeprecations] = useState(true);
  const [newFeatures, setNewFeatures] = useState(false);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-md">
      <h3 className="font-semibold mb-3">📡 API Change Notifications</h3>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="your@email.com"
        className="w-full text-sm px-3 py-1.5 border rounded mb-3 dark:bg-gray-800 dark:border-gray-600" />
      <div className="space-y-2 mb-3">
        {[
          { label: "Breaking changes", checked: breaking, set: setBreaking },
          { label: "Deprecations", checked: deprecations, set: setDeprecations },
          { label: "New features", checked: newFeatures, set: setNewFeatures },
        ].map(p => (
          <label key={p.label} className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={p.checked} onChange={e => p.set(e.target.checked)} />
            {p.label}
          </label>
        ))}
      </div>
      <p className="text-xs text-gray-400 mb-3">Versions: {versions.join(", ")}</p>
      <button onClick={() => email && onSubscribe(email, { breaking, deprecations, new: newFeatures })}
        className="w-full py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Subscribe</button>
    </div>
  );
}
