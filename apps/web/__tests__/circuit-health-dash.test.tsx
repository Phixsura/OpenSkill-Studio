import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitHealthDash } from "@/components/circuit-health-dash";

describe("CircuitHealthDash", () => {
  it("renders", () => {
    const { container } = render(
      <CircuitHealthDash overall="critical" openPct={33.3} criticalOpen={["payment"]}
        circuits={[
          { service: "api", state: "closed", critical: false },
          { service: "payment", state: "open", critical: true },
          { service: "cache", state: "half-open", critical: false },
        ]} />
    );
    expect(container.textContent).toContain("Circuit Health");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("33.3% open");
    expect(container.textContent).toContain("Critical: payment");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("cache");
  });
});
