import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookRetryV9Panel } from "@/components/fleet-webhook-retry-v9-panel";
describe("FleetWebhookRetryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookRetryV9Panel queues={10} deadLetter={0} />);
    expect(container.textContent).toContain("Webhook Retry v9");
}); });
