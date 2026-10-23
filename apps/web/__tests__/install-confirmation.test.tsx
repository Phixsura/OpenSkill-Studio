import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallConfirmation } from "@/components/install-confirmation";

describe("InstallConfirmation", () => {
  it("renders confirmation", () => {
    const onDone = vi.fn();
    const { container, getByText } = render(
      <InstallConfirmation appName="Slack Bot" appIcon="💬" version="2.1.0"
        permissions={["read:profile", "webhooks"]} webhookConfigured={true}
        nextSteps={[{ label: "Configure settings", path: "/settings" }]}
        onStep={vi.fn()} onDone={onDone} />
    );
    expect(container.textContent).toContain("Slack Bot Installed!");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("2 permissions granted");
    expect(container.textContent).toContain("Webhook configured");
    expect(container.textContent).toContain("Configure settings");
    fireEvent.click(getByText("Go to Dashboard"));
    expect(onDone).toHaveBeenCalled();
  });
});
