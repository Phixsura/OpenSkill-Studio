import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookFilterV9Panel } from "@/components/fleet-webhook-filter-v9-panel";
describe("FleetWebhookFilterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookFilterV9Panel filters={30} passed={100000} />);
    expect(container.textContent).toContain("Webhook Filter v9");
}); });
