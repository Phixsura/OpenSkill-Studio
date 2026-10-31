import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionStatusPage } from "@/components/extension-status-page";

const mockComponents = [
  { name: "API Gateway", status: "operational" as const },
  { name: "Webhook Delivery", status: "degraded" as const },
  { name: "Sandbox Runtime", status: "operational" as const },
];

const mockIncidents = [
  { id: "i1", title: "Webhook delivery delays", status: "monitoring" as const,
    severity: "minor" as const, createdAt: "2h ago", updatedAt: "30m ago",
    updates: [
      { message: "Investigating delivery delays", timestamp: "2h ago" },
      { message: "Root cause identified: queue backlog", timestamp: "1h ago" },
    ] },
];

describe("ExtensionStatusPage", () => {
  it("renders overall status", () => {
    const { container } = render(
      <ExtensionStatusPage extensionName="Slack Bot" components={mockComponents}
        incidents={mockIncidents} overallUptime={99.95} />
    );
    expect(container.textContent).toContain("Slack Bot Status");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("1 Active Incident");
  });

  it("renders components with status", () => {
    const { container } = render(
      <ExtensionStatusPage extensionName="Test" components={mockComponents}
        incidents={[]} overallUptime={100} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("degraded");
  });

  it("shows all operational when no issues", () => {
    const allOp = mockComponents.map((c) => ({ ...c, status: "operational" as const }));
    const { container } = render(
      <ExtensionStatusPage extensionName="Test" components={allOp}
        incidents={[]} overallUptime={100} />
    );
    expect(container.textContent).toContain("All Systems Operational");
  });

  it("renders incident updates", () => {
    const { container } = render(
      <ExtensionStatusPage extensionName="Test" components={mockComponents}
        incidents={mockIncidents} overallUptime={99.9} />
    );
    expect(container.textContent).toContain("Webhook delivery delays");
    expect(container.textContent).toContain("queue backlog");
  });
});
