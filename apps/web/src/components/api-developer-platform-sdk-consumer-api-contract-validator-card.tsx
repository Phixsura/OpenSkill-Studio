"use client";

import { useState } from "react";

interface ContractInfo {
  contractId: string;
  endpoint: string;
  version: string;
  fieldCount: number;
  passRate: number;
}

export default function ContractValidatorCard() {
  const [contracts] = useState<ContractInfo[]>([
    { contractId: "c1", endpoint: "/api/users", version: "v3", fieldCount: 8, passRate: 99.2 },
    { contractId: "c2", endpoint: "/api/orders", version: "v2", fieldCount: 12, passRate: 95.5 },
    { contractId: "c3", endpoint: "/api/products", version: "v1", fieldCount: 6, passRate: 100 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Contract Validator
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Schema contract testing with diff detection
      </p>

      <div className="mt-4 space-y-2">
        {contracts.map((c) => (
          <div key={c.contractId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{c.endpoint}</span>
              <span className="ml-2 text-xs text-zinc-400">{c.version}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">{c.fieldCount} fields</span>
              <span className={c.passRate >= 99 ? "text-green-600 dark:text-green-400" : "text-amber-600 dark:text-amber-400"}>
                {c.passRate}%
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {contracts.length} contracts registered
      </div>
    </div>
  );
}
