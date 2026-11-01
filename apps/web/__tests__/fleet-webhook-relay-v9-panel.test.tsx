import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookRelayV9Panel } from "@/components/fleet-webhook-relay-v9-panel";
describe("FleetWebhookRelayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookRelayV9Panel endpoints={30} delivered={100000} />);
    expect(container.textContent).toContain("Webhook Relay v9");
}); });
