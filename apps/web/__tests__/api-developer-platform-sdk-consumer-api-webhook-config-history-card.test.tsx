import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-webhook-config-history-card";

describe("WebhookConfigHistoryCard", () => {
  it("shows changes", () => {
    const changes = [{ id: "ch1", field: "url", oldValue: "https://old.com", newValue: "https://new.com", changedBy: "admin", timestamp: "12:00" }];
    const { container } = render(<Card webhookId="w1" totalChanges={5} mostChangedField="url" changes={changes} appName="App" />);
    expect(container.textContent).toContain("Config History");
    expect(container.textContent).toContain("url");
    expect(container.textContent).toContain("https://old.com");
    expect(container.textContent).toContain("https://new.com");
    expect(container.textContent).toContain("Most changed: url");
  });
  it("shows empty", () => {
    const { container } = render(<Card webhookId="w1" totalChanges={0} mostChangedField="" changes={[]} appName="App" />);
    expect(container.textContent).toContain("No config changes");
  });
});
