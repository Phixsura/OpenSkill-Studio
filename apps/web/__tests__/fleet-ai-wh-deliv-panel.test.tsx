import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWhDelivPanel } from "@/components/fleet-ai-wh-deliv-panel";
describe("FleetAiWhDelivPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWhDelivPanel systems={4} active={4} sent={5000000} delivered={4999000} failed={1000} rate={99.98} />);
    expect(container.textContent).toContain("Webhook Delivery");
}); });
