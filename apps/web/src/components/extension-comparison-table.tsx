"use client";

interface ExtensionCompare {
  id: string;
  name: string;
  icon: string;
  version: string;
  rating: number;
  downloads: number;
  price: string;
  features: Record<string, boolean | string>;
}

export function ExtensionComparisonTable({
  extensions,
  featureLabels,
  onSelect,
}: {
  extensions: ExtensionCompare[];
  featureLabels: { key: string; label: string }[];
  onSelect?: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⚖️ Compare Extensions</h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="text-left px-4 py-3 text-gray-500 w-40">Feature</th>
              {extensions.map((ext) => (
                <th key={ext.id} className="px-4 py-3 text-center min-w-40">
                  <div className="text-2xl mb-1">{ext.icon}</div>
                  <div className="font-bold">{ext.name}</div>
                  <div className="text-xs text-gray-400">v{ext.version}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Stats rows */}
            <CompareRow label="Rating" values={extensions.map((e) => `★ ${e.rating.toFixed(1)}`)} />
            <CompareRow label="Downloads" values={extensions.map((e) => e.downloads.toLocaleString())} />
            <CompareRow label="Price" values={extensions.map((e) => e.price)} />

            {/* Feature rows */}
            {featureLabels.map((feat) => (
              <tr key={feat.key} className="border-b dark:border-gray-800">
                <td className="px-4 py-2 text-gray-500">{feat.label}</td>
                {extensions.map((ext) => {
                  const val = ext.features[feat.key];
                  return (
                    <td key={ext.id} className="px-4 py-2 text-center">
                      {typeof val === "boolean" ? (
                        <span className={val ? "text-green-500" : "text-gray-300"}>
                          {val ? "✅" : "—"}
                        </span>
                      ) : (
                        <span className="text-sm">{val || "—"}</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}

            {/* Action row */}
            <tr>
              <td className="px-4 py-3" />
              {extensions.map((ext) => (
                <td key={ext.id} className="px-4 py-3 text-center">
                  <button
                    onClick={() => onSelect?.(ext.id)}
                    className="rounded-lg bg-blue-600 text-white px-4 py-1.5 text-xs font-medium"
                  >
                    Select
                  </button>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CompareRow({ label, values }: { label: string; values: string[] }) {
  return (
    <tr className="border-b dark:border-gray-800">
      <td className="px-4 py-2 font-medium text-gray-500">{label}</td>
      {values.map((v, i) => (
        <td key={i} className="px-4 py-2 text-center">{v}</td>
      ))}
    </tr>
  );
}
