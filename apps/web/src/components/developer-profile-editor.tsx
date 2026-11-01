"use client";

import { useState } from "react";

interface ProfileData { display_name: string; slug: string; bio: string; support_email: string; website: string; }
interface DeveloperProfileEditorProps { profile: ProfileData; completeness: number; onSave: (profile: ProfileData) => void; }

export function DeveloperProfileEditor({ profile, completeness, onSave }: DeveloperProfileEditorProps) {
  const [data, setData] = useState(profile);
  const update = (key: keyof ProfileData, value: string) => setData({ ...data, [key]: value });

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Developer Profile</h3>
        <span className="text-xs text-gray-400">{completeness}% complete</span>
      </div>
      <div className="mt-3 space-y-3">
        {(["display_name", "slug", "bio", "support_email", "website"] as const).map(key => (
          <div key={key}>
            <label className="block text-xs font-medium text-gray-500 capitalize">{key.replace("_", " ")}</label>
            {key === "bio" ? (
              <textarea value={data[key]} onChange={e => update(key, e.target.value)} rows={3}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
            ) : (
              <input value={data[key]} onChange={e => update(key, e.target.value)}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
            )}
          </div>
        ))}
      </div>
      <button onClick={() => onSave(data)} className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">Save Profile</button>
    </div>
  );
}
