import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GcMetricsCard } from "@/components/gc-metrics-card";

describe("GcMetricsCard", () => {
  it("renders metrics", () => {
    const { container } = render(
      <GcMetricsCard total={50} avgPauseMs={15} maxPauseMs={250} gcPressure="medium"
        byGeneration={{ young: 45, full: 5 }}
        suggestions={[{ action: "use_concurrent_gc", reason: "Long pauses" }]} />
    );
    expect(container.textContent).toContain("GC Metrics");
    expect(container.textContent).toContain("medium pressure");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("250ms");
    expect(container.textContent).toContain("use_concurrent_gc");
  });
});
