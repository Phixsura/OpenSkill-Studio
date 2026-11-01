import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNotifHubPanel } from "@/components/fleet-ai-notif-hub-panel";
describe("FleetAiNotifHubPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNotifHubPanel hubs={3} active={3} channels={20} sent={10000000} deliveryRate={99.9} />);
    expect(container.textContent).toContain("Notification Hub");
}); });
