"use client";

import { useState } from "react";

interface DataRecord {
  [key: string]: unknown;
}

export function OutputFormatterPanel({
  data,
  formattedOutput,
  onFormat,
  onCopy,
}: {
  data: DataRecord[];
  formattedOutput: string;
  onFormat?: (format: string, fields: string[]) => void;
  onCopy?: () => void;
}) {
  const [format, setFormat] = useState<string>("json");
  const [selectedFields, setSelectedFields] = useState<string[]>([]);

  const allFields = data.length > 0 ? Object.keys(data[0]) : [];

  const toggleField = (f: string) => {
    setSelectedFields((prev) =>
      prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]
    );
  };

  const formats = [
    { value: "json", label: "JSON", icon: "📋" },
    { value: "csv", label: "CSV", icon: "📊" },
    { value: "markdown", label: "Markdown", icon: "📝" },
    { value: "html", label: "HTML Table", icon: "🌐" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📤 Output Formatter</h2>

      <div className="flex gap-1">
        {formats.map((f) => (
          <button key={f.value} onClick={() => setFormat(f.value)}
            className={`text-xs px-3 py-1.5 rounded-lg ${format === f.value ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f.icon} {f.label}
          </button>
        ))}
      </div>

      {allFields.length > 0 && (
        <div>
          <span className="text-xs text-gray-500">Select fields:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {allFields.map((f) => (
              <button key={f} onClick={() => toggleField(f)}
                className={`text-xs px-2 py-0.5 rounded-full border ${
                  selectedFields.includes(f) ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 dark:border-gray-600"
                }`}>{f}</button>
            ))}
          </div>
        </div>
      )}

      <button onClick={() => onFormat?.(format, selectedFields.length > 0 ? selectedFields : allFields)}
        className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg">
        Format as {format.toUpperCase()}
      </button>

      {formattedOutput && (
        <div className="relative">
          <button onClick={onCopy}
            className="absolute top-2 right-2 text-xs bg-gray-700 text-white px-2 py-1 rounded z-10">Copy</button>
          <pre className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 text-xs text-green-400 font-mono overflow-x-auto max-h-64">
            {formattedOutput}
          </pre>
        </div>
      )}
    </div>
  );
}
