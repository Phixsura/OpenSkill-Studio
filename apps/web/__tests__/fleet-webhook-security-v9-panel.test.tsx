import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookSecurityV9Panel } from "@/components/fleet-webhook-security-v9-panel";
describe("FleetWebhookSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookSecurityV9Panel endpoints={30} signed={30} />);
    expect(container.textContent).toContain("Webhook Security v9");
}); });
