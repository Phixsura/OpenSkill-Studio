import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookEventDeduplicationCard from "../src/components/api-developer-api-api-webhook-event-deduplication-card";

describe("APIDeveloperAPIApiWebhookEventDeduplicationCard", () => {
  it("shows dedup stats", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookEventDeduplicationCard stats={{ active_hashes: 5000, duplicates_caught: 1200 }} appName="App" />);
    expect(container.textContent).toContain("Event Deduplication");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("19%");
  });
});
