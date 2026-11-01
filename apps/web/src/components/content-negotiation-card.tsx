"use client";

interface FormatInfo {
  media_type: string;
  quality: number;
  charset: string;
}

interface ContentNegotiationCardProps {
  formats: FormatInfo[];
  defaultFormat: string;
  appName: string;
}

export default function ContentNegotiationCard({
  formats,
  defaultFormat,
  appName,
}: ContentNegotiationCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📄 Content Negotiation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{formats.length} formats</span>
      </div>

      {formats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No formats registered</p>
      ) : (
        <div className="space-y-1.5">
          {formats.map((f) => (
            <div
              key={f.media_type}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {f.media_type}
                </span>
                {f.media_type === defaultFormat && (
                  <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                    default
                  </span>
                )}
              </div>
              <div className="text-[10px] text-gray-400">
                q={f.quality} · {f.charset}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
