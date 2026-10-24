import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitFsmPanel } from "@/components/circuit-fsm-panel";
describe("CircuitFsmPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CircuitFsmPanel state="open" failures={5}
        transitions={[
          { from: "closed", to: "open", reason: "failure_threshold_met" },
        ]} />
    );
    expect(container.textContent).toContain("Circuit FSM");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("5 failures");
    expect(container.textContent).toContain("closed → open");
    expect(container.textContent).toContain("failure_threshold_met");
  });
});
