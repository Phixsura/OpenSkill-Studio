"use client";

interface FieldInfo { name: string; field_type: string; required: boolean; }
interface SchemaInfo { schema_id: string; fields: FieldInfo[]; }
interface Props { schemas: SchemaInfo[]; appName: string; }

export default function APIDeveloperAPIApiPayloadSchemaValidatorCard({ schemas, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Schema Validator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas</p>
      ) : (
        <div className="space-y-2">
          {schemas.map((s) => (
            <div key={s.schema_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{s.schema_id}</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {s.fields.map((f) => (
                  <span key={f.name} className={`rounded px-1 py-0.5 text-[9px] ${f.required ? "bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200" : "bg-gray-100 text-gray-500 dark:bg-gray-700"}`}>{f.name}: {f.field_type}{f.required ? "*" : ""}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
