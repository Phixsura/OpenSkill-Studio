import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionInstallWizard } from "@/components/extension-install-wizard";

const mockConfig = {
  extensionName: "Slack Bot", extensionIcon: "💬", version: "2.1.0",
  permissions: ["Read Projects", "Send Notifications"],
  configFields: [
    { key: "webhook_url", label: "Webhook URL", placeholder: "https://...", required: true },
    { key: "channel", label: "Channel", placeholder: "#general", required: false },
  ],
};

describe("ExtensionInstallWizard", () => {
  it("renders first step with permissions", () => {
    const { container } = render(<ExtensionInstallWizard config={mockConfig} />);
    expect(container.textContent).toContain("Install Slack Bot");
    expect(container.textContent).toContain("Read Projects");
    expect(container.textContent).toContain("Send Notifications");
  });

  it("blocks next until permissions accepted", () => {
    const { getByText } = render(<ExtensionInstallWizard config={mockConfig} />);
    const next = getByText("Next →");
    expect(next.hasAttribute("disabled")).toBe(true);
  });

  it("proceeds through steps", () => {
    const { getByText, container } = render(<ExtensionInstallWizard config={mockConfig} />);
    // Accept permissions
    fireEvent.click(container.querySelector('input[type="checkbox"]')!);
    fireEvent.click(getByText("Next →"));
    // Now on config step
    expect(container.textContent).toContain("Webhook URL");
  });

  it("shows cancel on first step", () => {
    const onCancel = vi.fn();
    const { getByText } = render(<ExtensionInstallWizard config={mockConfig} onCancel={onCancel} />);
    fireEvent.click(getByText("Cancel"));
    expect(onCancel).toHaveBeenCalled();
  });
});
