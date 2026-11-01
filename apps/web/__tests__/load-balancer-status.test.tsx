import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadBalancerStatus } from "@/components/load-balancer-status";

describe("LoadBalancerStatus", () => {
  it("renders instances", () => {
    const instances = [
      { id: "inst-1", status: "healthy", weight_pct: 50 },
      { id: "inst-2", status: "unhealthy", weight_pct: 50 },
    ];
    const { container } = render(<LoadBalancerStatus instances={instances} healthy={1} total={2} />);
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("inst-1");
  });
});
