import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIIntegrationHubCard from "../src/components/api-developer-api-integration-hub-card";

const integrations = [
  { integration_id: "i1", name: "Slack Alerts", provider: "slack", status: "connected", event_count: 500 },
  { integration_id: "i2", name: "GitHub Sync", provider: "github", status: "disconnected", event_count: 0 },
];

describe("APIDeveloperAPIIntegrationHubCard", () => {
  it("shows integrations", () => {
    const { container } = render(<APIDeveloperAPIIntegrationHubCard integrations={integrations} appName="App" />);
    expect(container.textContent).toContain("Integration Hub");
    expect(container.textContent).toContain("1/2 connected");
    expect(container.textContent).toContain("Slack Alerts");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("500 events");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIIntegrationHubCard integrations={[]} appName="App" />);
    expect(container.textContent).toContain("No integrations");
  });
});
