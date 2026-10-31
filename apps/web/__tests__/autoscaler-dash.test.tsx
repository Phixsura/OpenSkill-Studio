import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoscalerDash } from "@/components/autoscaler-dash";

describe("AutoscalerDash", () => {
  it("renders", () => {
    const { container } = render(
      <AutoscalerDash totalReplicas={8} avgCpu={60}
        services={[
          { name: "api", replicas: 4, cpuPct: 85, action: "scale_up" },
          { name: "worker", replicas: 4, cpuPct: 35, action: "no_change" },
        ]} />
    );
    expect(container.textContent).toContain("Autoscaler");
    expect(container.textContent).toContain("8 replicas");
    expect(container.textContent).toContain("60% avg CPU");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("scale up");
    expect(container.textContent).toContain("no change");
  });
});
