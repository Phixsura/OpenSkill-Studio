import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSlaV3Panel } from "@/components/fleet-ai-plat-sla-v3-panel";
describe("FleetAiPlatSlaV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSlaV3Panel managers={3} active={3} slas={200} met={200} breached={0} credits={0} />);
    expect(container.textContent).toContain("SLA v3");
}); });
