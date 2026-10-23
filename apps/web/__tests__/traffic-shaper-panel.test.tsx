import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficShaperPanel } from "@/components/traffic-shaper-panel";

describe("TrafficShaperPanel", () => {
  it("renders shaper", () => {
    const { container } = render(
      <TrafficShaperPanel totalWeight={100} rules={[
        { name: "stable", target: "v1", weight: 90, pct: 90 },
        { name: "canary", target: "v2", weight: 10, pct: 10 },
      ]} />
    );
    expect(container.textContent).toContain("Traffic Shaping");
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("canary");
    expect(container.textContent).toContain("→ v2");
  });
});
