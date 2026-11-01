import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiWebhookV9Panel } from "@/components/fleet-api-webhook-v9-panel";
describe("FleetApiWebhookV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiWebhookV9Panel webhooks={50} delivered={50000} />);
    expect(container.textContent).toContain("API Webhook v9");
}); });
