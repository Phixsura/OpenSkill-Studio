import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatDoraV3Panel } from "@/components/fleet-ai-plat-dora-v3-panel";
describe("FleetAiPlatDoraV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatDoraV3Panel freq={200} lead={3} fail={0.2} mttr={5} trend="improving" classification="Elite" />);
    expect(container.textContent).toContain("DORA v3");
    expect(container.textContent).toContain("Elite");
}); });
