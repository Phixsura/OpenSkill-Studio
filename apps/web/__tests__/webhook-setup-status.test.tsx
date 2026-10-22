import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookSetupStatus } from "@/components/webhook-setup-status";

describe("WebhookSetupStatus", () => {
  it("shows complete", () => {
    const { container } = render(<WebhookSetupStatus configured={true} secretSet={true} subscriptionCount={3} setupComplete={true} />);
    expect(container.textContent).toContain("Webhook Ready");
    expect(container.textContent).toContain("3 events");
  });
  it("shows incomplete", () => {
    const { container } = render(<WebhookSetupStatus configured={false} secretSet={false} subscriptionCount={0} setupComplete={false} />);
    expect(container.textContent).toContain("Webhook Setup");
    expect(container.textContent).toContain("⬜");
  });
});
