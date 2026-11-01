import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogAggregatorView } from "@/components/log-aggregator-view";

describe("LogAggregatorView", () => {
  const logs = [
    { source: "api", level: "error", message: "DB timeout", timestamp: "2026-10-23T12:01:00" },
    { source: "worker", level: "info", message: "Job done", timestamp: "2026-10-23T12:00:30" },
  ];
  it("renders", () => {
    const { container } = render(
      <LogAggregatorView logs={logs} totalLogs={2} bySource={{ api: 1, worker: 1 }}
        byLevel={{ error: 1, info: 1 }} hasErrors={true} />
    );
    expect(container.textContent).toContain("Aggregated Logs");
    expect(container.textContent).toContain("⚠️ Errors detected");
    expect(container.textContent).toContain("DB timeout");
    expect(container.textContent).toContain("api: 1");
  });
});
