import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResourceOptimizerV9Panel } from "@/components/fleet-resource-optimizer-v9-panel";
describe("FleetResourceOptimizerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetResourceOptimizerV9Panel recs={50} savings={10000} />);
    expect(container.textContent).toContain("Resource Optimizer v9");
}); });
