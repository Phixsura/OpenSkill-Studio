import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPage } from "@/components/status-page";

describe("StatusPage", () => {
  const services = [
    { name: "API", status: "operational", icon: "🟢", uptime_pct: 99.99, response_ms: 45 },
    { name: "Database", status: "degraded", icon: "🟡", uptime_pct: 99.5, response_ms: null },
  ];
  it("renders services and overall", () => {
    const { container } = render(
      <StatusPage services={services} overall="degraded" overallIcon="🟡" incidents={[]} />
    );
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("45ms");
  });
  it("shows incidents", () => {
    const incidents = [{ title: "DB slow", status: "investigating", timestamp: "2026-01-01" }];
    const { container } = render(
      <StatusPage services={[]} overall="degraded" overallIcon="🟡" incidents={incidents} />
    );
    expect(container.textContent).toContain("DB slow");
    expect(container.textContent).toContain("investigating");
  });
});
