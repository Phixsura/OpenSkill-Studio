import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaBreachPanel } from "@/components/sla-breach-panel";
describe("SlaBreachPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SlaBreachPanel totalServices={3} allMet={false}
        breaches={[{ service: "db", target: 99.9, actual: 98.5, gap: 1.4, severity: "critical" }]} />
    );
    expect(container.textContent).toContain("SLA Breaches");
    expect(container.textContent).toContain("1 breached");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("gap: 1.4%");
  });
});
