import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLatencyBudgetV9Panel } from "@/components/fleet-latency-budget-v9-panel";
describe("FleetLatencyBudgetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLatencyBudgetV9Panel services={100} p99={50} />);
    expect(container.textContent).toContain("Latency Budget v9");
}); });
