"use client";

interface ApiVer { version: string; status: string; changelog: string[]; }
const statusBadge: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  deprecated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400",
};

export function ApiVersionSelector({ versions, selected, onSelect }: {
  versions: ApiVer[]; selected: string; onSelect?: (v: string) => void;
}) {
  return (
    <div className="space-y-2">
      {versions.map(v => (
        <button key={v.version} onClick={() => onSelect?.(v.version)}
          className={`w-full text-left border rounded-xl p-3 flex items-center justify-between ${
            selected === v.version ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"
          } ${v.status === "sunset" ? "opacity-50" : ""}`}
          disabled={v.status === "sunset"}>
          <div>
            <span className="font-bold text-sm">{v.version}</span>
            {v.changelog.length > 0 && <span className="text-xs text-gray-500 ml-2">{v.changelog[0]}</span>}
          </div>
          <span className={`text-xs px-2 py-0.5 rounded-full ${statusBadge[v.status] || ""}`}>{v.status}</span>
        </button>
      ))}
    </div>
  );
}
