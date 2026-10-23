import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HealthProbeDashboard } from "@/components/health-probe-dashboard";

describe("HealthProbeDashboard", () => {
  const services = [
    { service: "API", healthy: true, checks_passed: 2, checks_failed: 0, latency_ms: 20,
      details: [{ name: "db", status: "pass" }, { name: "cache", status: "pass" }] },
  ];
  it("renders", () => {
    const { container } = render(
      <HealthProbeDashboard services={services} overallStatus="healthy"
        checkedAt="2026-10-23T12:00:00" onRefresh={vi.fn()} />
    );
    expect(container.textContent).toContain("Health Probes");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("20ms");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("db");
  });
  it("refresh", () => {
    const fn = vi.fn();
    const { container } = render(
      <HealthProbeDashboard services={services} overallStatus="healthy"
        checkedAt="2026-10-23T12:00:00" onRefresh={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Refresh")!);
    expect(fn).toHaveBeenCalled();
  });
});
