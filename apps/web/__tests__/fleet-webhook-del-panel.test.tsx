import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookDelPanel } from "@/components/fleet-webhook-del-panel";
describe("FleetWebhookDelPanel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookDelPanel delivered={1985} failed={15} successRate={99.2} reliable={true} />);
    expect(container.textContent).toContain("Webhook Delivery");
    expect(container.textContent).toContain("99.2%");
}); });
