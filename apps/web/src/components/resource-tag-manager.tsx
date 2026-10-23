"use client";

interface TaggedResource { id: string; tags: Record<string, string>; }
interface ResourceTagManagerProps { resources: TaggedResource[]; tagKeys: string[];
  onTag: (id: string, key: string, value: string) => void; }

export function ResourceTagManager({ resources, tagKeys, onTag }: ResourceTagManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Resource Tags</h3>
        <span className="text-xs text-gray-400">{resources.length} resources · {tagKeys.length} keys</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
            <th className="p-3 text-left">Resource</th>
            {tagKeys.map(k => <th key={k} className="p-3 text-left">{k}</th>)}
          </tr></thead>
          <tbody>
            {resources.map(r => (
              <tr key={r.id} className="border-b last:border-0 dark:border-gray-700">
                <td className="p-3 font-mono text-xs">{r.id}</td>
                {tagKeys.map(k => (
                  <td key={k} className="p-3">
                    {r.tags[k]
                      ? <span className="text-xs px-1.5 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded">{r.tags[k]}</span>
                      : <button onClick={() => onTag(r.id, k, "")} className="text-xs text-gray-300 hover:text-gray-500">+</button>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
