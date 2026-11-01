import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiUsageDashboard } from "@/components/api-usage-dashboard";

const mockKeys = [
  { keyName: "Production", keyPrefix: "osk_abc1", callsToday: 850, callsThisMonth: 24000, quota: 1000, lastUsed: "2m ago", status: "active" as const },
  { keyName: "Staging", keyPrefix: "osk_xyz2", callsToday: 50, callsThisMonth: 1200, quota: 500, lastUsed: "1h ago", status: "active" as const },
];

const mockEndpoints = [
  { endpoint: "/api/v1/extensions", method: "GET", calls: 12500, avgLatencyMs: 45, errorRate: 0.2 },
  { endpoint: "/api/v1/submissions", method: "POST", calls: 3400, avgLatencyMs: 120, errorRate: 1.5 },
];

describe("ApiUsageDashboard", () => {
  it("renders total calls and period", () => {
    const { container } = render(
      <ApiUsageDashboard keys={mockKeys} endpoints={mockEndpoints} totalCalls={45000} periodLabel="Oct 2026" />
    );
    expect(container.textContent).toContain("45,000");
    expect(container.textContent).toContain("Oct 2026");
  });

  it("renders API keys with usage", () => {
    const { container } = render(
      <ApiUsageDashboard keys={mockKeys} endpoints={mockEndpoints} totalCalls={45000} periodLabel="Oct 2026" />
    );
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("osk_abc1");
    expect(container.textContent).toContain("active");
  });

  it("renders endpoint table", () => {
    const { container } = render(
      <ApiUsageDashboard keys={mockKeys} endpoints={mockEndpoints} totalCalls={45000} periodLabel="Oct 2026" />
    );
    expect(container.textContent).toContain("/api/v1/extensions");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("45ms");
  });
});
