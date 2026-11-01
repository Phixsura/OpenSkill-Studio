import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficSplitPanel } from "@/components/traffic-split-panel";
describe("TrafficSplitPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TrafficSplitPanel valid={true}
        splits={[{ version: "v1", pct: 90 }, { version: "v2", pct: 10 }]} />
    );
    expect(container.textContent).toContain("Traffic Split");
    expect(container.textContent).toContain("Valid (100%)");
    expect(container.textContent).toContain("v1: 90%");
    expect(container.textContent).toContain("v2: 10%");
  });
});
