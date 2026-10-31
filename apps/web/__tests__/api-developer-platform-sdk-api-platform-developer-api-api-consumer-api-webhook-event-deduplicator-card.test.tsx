import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-event-deduplicator-card";

describe("EventDeduplicatorCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card stats={{ checked: 10000, duplicates: 500, duplicate_rate: 5 }} windowMinutes={60} appName="App" />);
    expect(container.textContent).toContain("Event Deduplicator");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("5% dupes");
  });
  it("shows window", () => {
    const { container } = render(<Card stats={{ checked: 0, duplicates: 0, duplicate_rate: 0 }} windowMinutes={30} appName="App" />);
    expect(container.textContent).toContain("30m window");
  });
});
