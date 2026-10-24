"use client";

interface EventSchemaViewerProps {
  eventType: string;
  required: string[];
  optional: string[];
}

export function EventSchemaViewer({ eventType, required, optional }: EventSchemaViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-mono text-sm font-semibold">{eventType}</h4>
      <div className="space-y-2">
        {required.length > 0 && (
          <div>
            <span className="text-xs font-medium text-red-600">Required fields</span>
            <div className="mt-1 flex flex-wrap gap-1">
              {required.map(f => <code key={f} className="rounded bg-red-50 px-1.5 py-0.5 text-xs dark:bg-red-900/20">{f}</code>)}
            </div>
          </div>
        )}
        {optional.length > 0 && (
          <div>
            <span className="text-xs font-medium text-gray-500">Optional fields</span>
            <div className="mt-1 flex flex-wrap gap-1">
              {optional.map(f => <code key={f} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{f}</code>)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
