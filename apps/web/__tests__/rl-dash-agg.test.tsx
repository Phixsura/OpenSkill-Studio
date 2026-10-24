import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RlDashAgg } from "@/components/rl-dash-agg";

describe("RlDashAgg", () => {
  it("renders", () => {
    const { container } = render(
      <RlDashAgg totalDenied={3} totalEvents={5}
        keys={[
          { key: "u2", allowed: 0, denied: 2, total: 2, denyRate: 100 },
          { key: "u1", allowed: 2, denied: 1, total: 3, denyRate: 33.3 },
        ]} />
    );
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("3 denied / 5 total");
    expect(container.textContent).toContain("u2");
    expect(container.textContent).toContain("100% denied");
  });
});
