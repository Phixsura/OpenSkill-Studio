"use client";

interface SchemaStats {
  types: number;
  fields: number;
  queries: number;
  mutations: number;
}

interface GraphQLTypeInfo {
  type_name: string;
  kind: string;
  field_count: number;
}

interface APIGraphQLSchemaCardProps {
  stats: SchemaStats;
  types: GraphQLTypeInfo[];
  appName: string;
}

export default function APIGraphQLSchemaCard({ stats, types, appName }: APIGraphQLSchemaCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">◈ GraphQL Schema</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{stats.types} types · {stats.fields} fields</span>
      </div>

      <div className="mb-3 grid grid-cols-2 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats.queries}</p>
          <p className="text-[9px] text-gray-500">queries</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats.mutations}</p>
          <p className="text-[9px] text-gray-500">mutations</p>
        </div>
      </div>

      {types.length > 0 && (
        <div className="space-y-1">
          {types.map((t) => (
            <div key={t.type_name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{t.kind}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{t.type_name}</span>
              </div>
              <span className="text-gray-400">{t.field_count} fields</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
