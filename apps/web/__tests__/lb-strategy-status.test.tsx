import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LbStrategyStatus } from "@/components/lb-strategy-status";

describe("LbStrategyStatus", () => {
  it("renders", () => {
    const { container } = render(
      <LbStrategyStatus strategy="weighted" totalRequests={10000}
        backends={[
          { name: "backend-1", weight: 3, requestCount: 7500 },
          { name: "backend-2", weight: 1, requestCount: 2500 },
        ]} />
    );
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("weighted");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("backend-1");
    expect(container.textContent).toContain("w:3");
    expect(container.textContent).toContain("7,500 reqs");
  });
});
