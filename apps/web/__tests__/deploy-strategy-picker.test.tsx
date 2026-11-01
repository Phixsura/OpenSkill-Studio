import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployStrategyPicker } from "@/components/deploy-strategy-picker";

describe("DeployStrategyPicker", () => {
  it("renders strategies", () => {
    const { container } = render(
      <DeployStrategyPicker recommended="blue_green" onSelect={vi.fn()}
        strategies={[
          { name: "rolling", description: "Gradual replace", downtime: false, rollbackSpeed: "fast", complexity: "low" },
          { name: "blue_green", description: "Instant switch", downtime: false, rollbackSpeed: "instant", complexity: "medium" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Strategy");
    expect(container.textContent).toContain("rolling");
    expect(container.textContent).toContain("blue green");
    expect(container.textContent).toContain("recommended");
    expect(container.textContent).toContain("Zero-downtime");
    expect(container.textContent).toContain("low");
  });
});
