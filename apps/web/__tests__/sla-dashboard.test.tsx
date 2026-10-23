import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaDashboard } from "@/components/sla-dashboard";

describe("SlaDashboard", () => {
  const results = [
    { metric: "uptime", target: 99.9, actual: 99.95, met: true, margin: 0.05, status: "pass" },
    { metric: "latency", target: 200, actual: 250, met: false, margin: -50, status: "fail" },
  ];
  it("renders SLA results", () => {
    const { container } = render(<SlaDashboard results={results} compliancePct={50} overall="non-compliant" />);
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("PASS");
    expect(container.textContent).toContain("latency");
    expect(container.textContent).toContain("FAIL");
    expect(container.textContent).toContain("50%");
  });
});
