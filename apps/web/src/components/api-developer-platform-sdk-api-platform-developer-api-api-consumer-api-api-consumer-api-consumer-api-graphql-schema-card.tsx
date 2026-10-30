"use client";

interface Field { name: string; type: string; deprecated: boolean; }
interface GQLType { name: string; kind: string; fields: Field[]; }
interface Props { types: GQLType[]; appName: string; }

const kindColors: Record<string, string> = {
  object: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  input: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  enum: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  interface: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchemaCard({ types, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">◈ GraphQL Schema</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {types.length} types</p>
      </div>
      {types.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No types registered</p>
      ) : (
        <div className="space-y-2">
          {types.map((t) => (
            <div key={t.name} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-2 text-[11px]">
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${kindColors[t.kind] ?? ""}`}>{t.kind}</span>
                <span className="font-semibold text-gray-700 dark:text-gray-300">{t.name}</span>
                <span className="text-[10px] text-gray-400">{t.fields.length} fields</span>
              </div>
              {t.fields.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {t.fields.slice(0, 6).map((f) => (
                    <span key={f.name} className={`text-[9px] ${f.deprecated ? "line-through text-gray-400" : "text-gray-500"}`}>{f.name}: {f.type}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
