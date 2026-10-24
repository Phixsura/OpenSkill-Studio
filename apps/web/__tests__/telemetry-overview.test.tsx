import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TelemetryOverview } from "@/components/telemetry-overview";

describe("TelemetryOverview", () => {
  it("renders telemetry", () => {
    const { container } = render(
      <TelemetryOverview totalSpans={10000} avgMs={45} p99Ms={250} errorRate={1.5}
        topOperations={[
          { operation: "GET /api/users", count: 5000, avgMs: 30 },
          { operation: "POST /api/data", count: 3000, avgMs: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Telemetry");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("250ms");
    expect(container.textContent).toContain("1.5%");
    expect(container.textContent).toContain("GET /api/users");
  });
});
