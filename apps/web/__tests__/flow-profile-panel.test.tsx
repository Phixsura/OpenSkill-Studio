import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FlowProfilePanel } from "@/components/flow-profile-panel";
describe("FlowProfilePanel", () => {
  it("renders", () => {
    const { container } = render(
      <FlowProfilePanel totalMs={75} spans={3} bottleneck="api" bottleneckMs={50}
        overheadMs={10} efficiencyPct={86.7} />
    );
    expect(container.textContent).toContain("Flow Profile");
    expect(container.textContent).toContain("75ms");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("86.7% efficient");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("10ms");
  });
});
