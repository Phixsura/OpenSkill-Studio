import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorTemplateWizard } from "@/components/connector-template-wizard";

const mockTemplates = [
  { id: "slack", name: "Slack", icon: "💬", category: "Messaging", description: "Connect to Slack", configFields: ["Webhook URL", "Channel"] },
  { id: "github", name: "GitHub", icon: "🐙", category: "DevTools", description: "Connect to GitHub", configFields: ["Token", "Repo"] },
];

describe("ConnectorTemplateWizard", () => {
  it("renders templates by category", () => {
    const { container } = render(<ConnectorTemplateWizard templates={mockTemplates} />);
    expect(container.textContent).toContain("New Connector");
    expect(container.textContent).toContain("Messaging");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("GitHub");
  });

  it("proceeds through steps", () => {
    const { getByText, container } = render(<ConnectorTemplateWizard templates={mockTemplates} />);
    // Select template
    fireEvent.click(getByText("Slack"));
    fireEvent.click(getByText("Next →"));
    // Now on step 1
    expect(container.textContent).toContain("Connector Name");
  });

  it("calls onCreate on final step", () => {
    const onCreate = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <ConnectorTemplateWizard templates={mockTemplates} onCreate={onCreate} />
    );
    fireEvent.click(getByText("Slack"));
    fireEvent.click(getByText("Next →"));
    fireEvent.change(getByPlaceholderText("My Slack Connector"), { target: { value: "My Slack" } });
    fireEvent.click(getByText("Next →"));
    fireEvent.click(getByText("🔌 Create Connector"));
    expect(onCreate).toHaveBeenCalledWith("slack", "My Slack", {});
  });
});
