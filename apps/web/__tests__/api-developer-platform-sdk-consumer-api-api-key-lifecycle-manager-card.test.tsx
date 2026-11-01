import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-api-key-lifecycle-manager-card";

describe("ApiKeyLifecycleManagerCard", () => {
  it("shows keys", () => {
    const keys = [{ id: "k1", label: "Main Key", status: "active", requestCount: 5000, createdAt: "2026-01", expiresAt: "2026-09", lastUsed: "5m ago" }];
    const { container } = render(<Card keys={keys} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Lifecycle");
    expect(container.textContent).toContain("Main Key");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("1 active / 1 total");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No API keys");
  });
});
