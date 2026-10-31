import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAntiaffinPanel } from "@/components/fleet-antiaffin-panel";
describe("FleetAntiaffinPanel", () => { it("renders", () => {
    const { container } = render(<FleetAntiaffinPanel total={10} withAa={8} colocatedRisk={1} haCompliant={false} />);
    expect(container.textContent).toContain("Anti-Affinity");
    expect(container.textContent).toContain("1 co-location");
}); });
