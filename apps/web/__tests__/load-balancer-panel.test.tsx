import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadBalancerPanel } from "@/components/load-balancer-panel";

describe("LoadBalancerPanel", () => {
  it("renders pool", () => {
    const { container } = render(
      <LoadBalancerPanel name="API Pool" algorithm="round_robin" capacityPct={67} healthy={2} total={3}
        backends={[
          { address: "10.0.0.1:8080", weight: 50, healthy: true },
          { address: "10.0.0.2:8080", weight: 30, healthy: true },
          { address: "10.0.0.3:8080", weight: 20, healthy: false },
        ]} />
    );
    expect(container.textContent).toContain("API Pool");
    expect(container.textContent).toContain("round robin");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("2/3 healthy");
    expect(container.textContent).toContain("10.0.0.1:8080");
  });
});
