import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SloDashPanel } from "@/components/slo-dash-panel";
describe("SloDashPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SloDashPanel meeting={1} atRisk={1} breaching={1} overallHealth="red"
        slos={[
          { name: "availability", current: 99.99, target: 99.9 },
          { name: "latency", current: 99.0, target: 99.5 },
        ]} />
    );
    expect(container.textContent).toContain("SLO Status");
    expect(container.textContent).toContain("1 meeting");
    expect(container.textContent).toContain("1 breaching");
    expect(container.textContent).toContain("availability");
    expect(container.textContent).toContain("99.99%");
  });
});
