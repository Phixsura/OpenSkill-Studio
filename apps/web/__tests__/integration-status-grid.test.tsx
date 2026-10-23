import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IntegrationStatusGrid } from "@/components/integration-status-grid";

describe("IntegrationStatusGrid", () => {
  it("renders integrations", () => {
    const { container } = render(
      <IntegrationStatusGrid connected={2} total={3} integrations={[
        { name: "Slack", provider: "slack", status: "connected", lastSync: "5m ago", icon: "💬" },
        { name: "Jira", provider: "jira", status: "disconnected", lastSync: "", icon: "📋" },
      ]} />
    );
    expect(container.textContent).toContain("Integrations");
    expect(container.textContent).toContain("2/3 connected");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("5m ago");
    expect(container.textContent).toContain("Disconnected");
  });
});
