import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetComputeOptimizerV9Panel } from "@/components/fleet-compute-optimizer-v9-panel";
describe("FleetComputeOptimizerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetComputeOptimizerV9Panel instances={200} savings={5000} />);
    expect(container.textContent).toContain("Compute Optimizer v9");
}); });
