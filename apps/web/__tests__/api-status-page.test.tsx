import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiStatusPage } from "@/components/api-status-page";

describe("ApiStatusPage", () => {
  const services = [
    { name: "API Gateway", status: "healthy", uptimePct: 99.99, avgLatencyMs: 45, errorRatePct: 0, icon: "🟢" },
    { name: "Database", status: "degraded", uptimePct: 99.5, avgLatencyMs: 120, errorRatePct: 2.5, icon: "🟡" },
  ];
  it("renders status page", () => {
    const { container } = render(
      <ApiStatusPage services={services} overall="degraded" avgLatencyMs={82}
        checkedAt="2026-01-01T12:00:00Z" />
    );
    expect(container.textContent).toContain("Partial Degradation");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("82ms");
    expect(container.textContent).toContain("2.5% err");
  });
});
