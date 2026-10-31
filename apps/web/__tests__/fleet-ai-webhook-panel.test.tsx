import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWebhookPanel } from "@/components/fleet-ai-webhook-panel";
describe("FleetAiWebhookPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWebhookPanel endpoints={20} active={20} delivered={5000000} failed={0} />);
    expect(container.textContent).toContain("AI Webhooks");
}); });
