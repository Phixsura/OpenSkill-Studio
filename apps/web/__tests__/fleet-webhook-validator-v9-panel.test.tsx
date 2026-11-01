import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebhookValidatorV9Panel } from "@/components/fleet-webhook-validator-v9-panel";
describe("FleetWebhookValidatorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWebhookValidatorV9Panel endpoints={20} validated={100000} />);
    expect(container.textContent).toContain("Webhook Validator v9");
}); });
