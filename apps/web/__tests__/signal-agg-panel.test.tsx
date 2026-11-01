import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SignalAggPanel } from "@/components/signal-agg-panel";
describe("SignalAggPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SignalAggPanel compositeScore={97} status="healthy" sources={3}
        signals={{ metrics: 99, logs: 100, traces: 98 }} />
    );
    expect(container.textContent).toContain("97");
    expect(container.textContent).toContain("HEALTHY");
    expect(container.textContent).toContain("3 sources");
    expect(container.textContent).toContain("metrics");
    expect(container.textContent).toContain("99%");
    expect(container.textContent).toContain("traces");
  });
});
