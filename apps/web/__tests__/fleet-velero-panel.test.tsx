import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVeleroPanel } from "@/components/fleet-velero-panel";
describe("FleetVeleroPanel", () => { it("renders", () => {
    const { container } = render(<FleetVeleroPanel total={10} completed={9} failed={1} latestAge={6} fresh={true} />);
    expect(container.textContent).toContain("Velero");
    expect(container.textContent).toContain("6h ago");
}); });
