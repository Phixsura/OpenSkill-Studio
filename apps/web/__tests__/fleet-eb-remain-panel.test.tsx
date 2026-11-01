import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEbRemainPanel } from "@/components/fleet-eb-remain-panel";
describe("FleetEbRemainPanel", () => { it("renders", () => {
    const { container } = render(<FleetEbRemainPanel remainingMin={33.2} remainingPct={76.9} status="safe" />);
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("76.9% remaining");
}); });
