import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatEvhubV2Panel } from "@/components/fleet-ai-plat-evhub-v2-panel";
describe("FleetAiPlatEvhubV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatEvhubV2Panel hubs={3} active={3} events={20000000000} topics={1000} consumers={5000} />);
    expect(container.textContent).toContain("Event Hub v2");
}); });
