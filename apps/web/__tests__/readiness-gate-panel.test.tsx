import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReadinessGatePanel } from "@/components/readiness-gate-panel";
describe("ReadinessGatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReadinessGatePanel ready={true} passed={2} total={3}
        checks={[
          { name: "database", ready: true, critical: true },
          { name: "cache", ready: true, critical: true },
          { name: "metrics", ready: false, critical: false },
        ]} />
    );
    expect(container.textContent).toContain("Readiness Gate");
    expect(container.textContent).toContain("Ready");
    expect(container.textContent).toContain("2/3");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("metrics");
    expect(container.textContent).toContain("optional");
  });
});
