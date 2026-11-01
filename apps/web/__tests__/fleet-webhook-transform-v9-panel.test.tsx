import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookTransformV9Panel } from "@/components/fleet-webhook-transform-v9-panel";
describe("FleetWebhookTransformV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookTransformV9Panel transforms={20} errors={0} />);
    expect(container.textContent).toContain("Webhook Transform v9");
}); });
