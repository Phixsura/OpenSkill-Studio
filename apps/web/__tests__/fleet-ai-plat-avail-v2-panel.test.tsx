import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatAvailV2Panel } from "@/components/fleet-ai-plat-avail-v2-panel";
describe("FleetAiPlatAvailV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatAvailV2Panel monitors={5} active={5} uptime={99.9999} downtime={0.1} nines={5} />);
    expect(container.textContent).toContain("Availability v2");
}); });
