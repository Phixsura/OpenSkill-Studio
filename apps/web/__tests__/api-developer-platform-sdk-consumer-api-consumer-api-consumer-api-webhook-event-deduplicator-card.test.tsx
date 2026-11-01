import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-consumer-api-webhook-event-deduplicator-card";

describe("WebhookEventDeduplicatorCard", () => {
  it("shows dedup stats", () => {
    const { container } = render(<Card trackedFingerprints={5000} ttlHours={24} maxEntries={100000} duplicatesBlocked={150} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Event Deduplication");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("TTL: 24h");
  });
  it("shows zero", () => {
    const { container } = render(<Card trackedFingerprints={0} ttlHours={1} maxEntries={1000} duplicatesBlocked={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
