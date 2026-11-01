import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWebhookV5Panel } from "@/components/fleet-ai-webhook-v5-panel";
describe("FleetAiWebhookV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiWebhookV5Panel systems={4} active={4} endpoints={10000} delivered={200000000} failed={1000} rate={99.99} />);
    expect(container.textContent).toContain("Webhook v5");
}); });
