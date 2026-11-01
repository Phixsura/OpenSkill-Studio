import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAuroraPanel } from "@/components/fleet-aurora-panel";
describe("FleetAuroraPanel", () => { it("renders", () => {
    const { container } = render(<FleetAuroraPanel clusters={5} available={5} serverless={3} currentAcu={24} />);
    expect(container.textContent).toContain("Aurora");
    expect(container.textContent).toContain("3 serverless");
}); });
