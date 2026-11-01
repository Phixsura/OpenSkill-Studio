import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatAdoptPanel } from "@/components/fleet-ai-plat-adopt-panel";
describe("FleetAiPlatAdoptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatAdoptPanel trackers={3} active={3} signups={5000} activated={2500} retained={2000} conversion={50} />);
    expect(container.textContent).toContain("Platform Adoption");
}); });
