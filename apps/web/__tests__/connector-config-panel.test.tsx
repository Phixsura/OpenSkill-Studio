import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorConfigPanel } from "@/components/connector-config-panel";

const mockConnector = {
  id: "slack-001",
  name: "Slack Integration",
  icon: "💬",
  provider: "Slack Technologies",
  fields: [
    { key: "webhook_url", label: "Webhook URL", type: "url" as const, required: true, placeholder: "https://hooks.slack.com/..." },
    { key: "channel", label: "Channel", type: "text" as const, required: true, placeholder: "#general" },
    { key: "token", label: "Bot Token", type: "password" as const, required: false, description: "Optional bot token for rich messages" },
  ],
};

describe("ConnectorConfigPanel", () => {
  it("renders connector info and fields", () => {
    const { container } = render(<ConnectorConfigPanel connector={mockConnector} />);
    expect(container.textContent).toContain("Slack Integration");
    expect(container.textContent).toContain("Slack Technologies");
    expect(container.textContent).toContain("Webhook URL");
    expect(container.textContent).toContain("Channel");
    expect(container.textContent).toContain("Bot Token");
  });

  it("disables buttons when required fields empty", () => {
    const { getByText } = render(<ConnectorConfigPanel connector={mockConnector} />);
    const saveBtn = getByText("💾 Save Configuration");
    expect(saveBtn.hasAttribute("disabled")).toBe(true);
  });

  it("calls onSave with values", () => {
    const onSave = vi.fn();
    const { getByText, getAllByRole } = render(
      <ConnectorConfigPanel
        connector={mockConnector}
        initialValues={{ webhook_url: "https://test.com", channel: "#dev" }}
        onSave={onSave}
      />
    );
    fireEvent.click(getByText("💾 Save Configuration"));
    expect(onSave).toHaveBeenCalledWith({ webhook_url: "https://test.com", channel: "#dev" });
  });
});
