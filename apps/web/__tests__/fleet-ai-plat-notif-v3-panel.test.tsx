import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatNotifV3Panel } from "@/components/fleet-ai-plat-notif-v3-panel";
describe("FleetAiPlatNotifV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatNotifV3Panel systems={4} active={4} sent={5000000} channels={20} delivery={99.95} />);
    expect(container.textContent).toContain("Notification v3");
}); });
