import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObservabilityCostV9Panel } from "@/components/fleet-observability-cost-v9-panel";
describe("FleetObservabilityCostV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetObservabilityCostV9Panel sources={10} cost={5000} />);
    expect(container.textContent).toContain("Observability Cost v9");
}); });
