"use client";

interface TransformInfo {
  transform_id: string;
  webhook_id: string;
  field_mapping_count: number;
  include_fields: string[] | null;
  exclude_fields: string[] | null;
  extra_header_count: number;
}

interface WebhookTransformCardProps {
  transforms: TransformInfo[];
  appName: string;
}

export default function WebhookTransformCard({ transforms, appName }: WebhookTransformCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Webhook Transforms
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{transforms.length} transforms</span>
      </div>

      {transforms.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No transforms configured</p>
      ) : (
        <div className="space-y-2">
          {transforms.map((t) => (
            <div
              key={t.transform_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                  {t.transform_id}
                </span>
                <span className="text-[11px] text-gray-400">{t.webhook_id}</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-2 text-[10px]">
                {t.field_mapping_count > 0 && (
                  <span className="rounded bg-blue-100 px-1.5 py-0.5 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                    {t.field_mapping_count} mappings
                  </span>
                )}
                {t.include_fields && (
                  <span className="rounded bg-green-100 px-1.5 py-0.5 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                    {t.include_fields.length} included
                  </span>
                )}
                {t.exclude_fields && (
                  <span className="rounded bg-red-100 px-1.5 py-0.5 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                    {t.exclude_fields.length} excluded
                  </span>
                )}
                {t.extra_header_count > 0 && (
                  <span className="rounded bg-purple-100 px-1.5 py-0.5 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                    {t.extra_header_count} headers
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
