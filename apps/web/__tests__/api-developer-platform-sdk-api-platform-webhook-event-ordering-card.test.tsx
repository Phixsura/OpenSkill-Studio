import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformWebhookEventOrderingCard from "../src/components/api-developer-platform-sdk-api-platform-webhook-event-ordering-card";

const partitions = [{ partition_key: "user-123", last_delivered_seq: 42, pending_count: 3, out_of_order_count: 1 }];

describe("Card", () => {
  it("shows ordering", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookEventOrderingCard partitions={partitions} outOfOrderCount={1} appName="App" />);
    expect(container.textContent).toContain("Event Ordering");
    expect(container.textContent).toContain("1 out of order");
    expect(container.textContent).toContain("user-123");
    expect(container.textContent).toContain("seq:42");
    expect(container.textContent).toContain("3 pending");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookEventOrderingCard partitions={[]} outOfOrderCount={0} appName="App" />);
    expect(container.textContent).toContain("No ordering data");
  });
});
