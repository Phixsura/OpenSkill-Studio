import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-key-metadata-card";

describe("ConsumerApiKeyMetadataCard", () => {
  it("shows keys", () => {
    const keys = [{ id: "k1", label: "Main Key", environment: "production", requestCount: 5000, lastUsed: "5m ago", tags: { team: "backend" } }];
    const { container } = render(<Card keys={keys} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Key Metadata");
    expect(container.textContent).toContain("Main Key");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("5m ago");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No API keys");
  });
});
