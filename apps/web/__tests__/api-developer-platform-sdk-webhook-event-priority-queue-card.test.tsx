import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKWebhookEventPriorityQueueCard from "../src/components/api-developer-platform-sdk-webhook-event-priority-queue-card";

describe("Card", () => {
  it("shows queue", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookEventPriorityQueueCard queueSize={25} processedCount={10000} priorityCounts={{ critical: 2, high: 5, normal: 15, low: 3 }} appName="App" />);
    expect(container.textContent).toContain("Event Priority Queue");
    expect(container.textContent).toContain("25 queued");
    expect(container.textContent).toContain("critical: 2");
    expect(container.textContent).toContain("10,000 processed");
  });
});
