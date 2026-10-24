import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTypeSafetyPanel } from "@/components/fleet-type-safety-panel";
describe("FleetTypeSafetyPanel", () => { it("renders", () => {
    const { container } = render(<FleetTypeSafetyPanel total={10} strictTyped={7} avgCoverage={85} typeSafe={true} />);
    expect(container.textContent).toContain("Type Safety");
    expect(container.textContent).toContain("85%");
}); });
