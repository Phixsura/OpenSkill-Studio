import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficShapeDash } from "@/components/traffic-shape-dash";

describe("TrafficShapeDash", () => {
  it("renders", () => {
    const { container } = render(
      <TrafficShapeDash trackedKeys={2} maxRequests={100} windowSeconds={60}
        entries={[
          { key: "user1", current: 50, limit: 100, remaining: 50, allowed: true },
          { key: "user2", current: 100, limit: 100, remaining: 0, allowed: false },
        ]} />
    );
    expect(container.textContent).toContain("Traffic Shaping");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("100/60s");
    expect(container.textContent).toContain("user1");
    expect(container.textContent).toContain("50/100");
  });
});
