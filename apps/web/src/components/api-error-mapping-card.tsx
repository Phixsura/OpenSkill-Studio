"use client";

interface MappingInfo {
  internal_code: string;
  public_code: string;
  http_status: number;
  occurrences: number;
}

interface APIErrorMappingCardProps {
  mappings: MappingInfo[];
  appName: string;
}

export default function APIErrorMappingCard({ mappings, appName }: APIErrorMappingCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Error Mapping</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{mappings.length} mappings</span>
      </div>

      {mappings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error mappings</p>
      ) : (
        <div className="space-y-1">
          {mappings.map((m) => (
            <div key={m.internal_code} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1">
                <span className="font-mono text-gray-500">{m.internal_code}</span>
                <span className="text-gray-400">→</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{m.public_code}</span>
                <span className={`text-[10px] ${m.http_status >= 500 ? "text-red-500" : "text-yellow-600"}`}>{m.http_status}</span>
              </div>
              {m.occurrences > 0 && <span className="text-gray-400">{m.occurrences}x</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
