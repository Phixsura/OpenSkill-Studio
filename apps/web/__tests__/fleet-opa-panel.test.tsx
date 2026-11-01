import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpaPanel } from "@/components/fleet-opa-panel";
describe("FleetOpaPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpaPanel policies={10} totalEval={15000} denied={600} avgLatency={2.5} />);
    expect(container.textContent).toContain("OPA Policies");
    expect(container.textContent).toContain("15,000 evals");
}); });
