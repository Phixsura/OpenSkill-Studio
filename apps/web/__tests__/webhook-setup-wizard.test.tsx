import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSetupWizard } from "@/components/webhook-setup-wizard";

describe("WebhookSetupWizard", () => {
  it("renders first step", () => {
    const { container } = render(
      <WebhookSetupWizard availableEvents={["app.installed"]}
        categories={{ App: ["app.installed"] }} onComplete={vi.fn()} />
    );
    expect(container.textContent).toContain("Setup Webhook");
    expect(container.textContent).toContain("Url");
    expect(container.querySelector("input")).toBeTruthy();
  });
});
