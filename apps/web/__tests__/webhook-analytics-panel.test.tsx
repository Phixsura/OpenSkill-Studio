import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookAnalyticsPanel } from "@/components/webhook-analytics-panel";

describe("WebhookAnalyticsPanel", () => {
  it("renders metrics", () => {
    const eventTypes = [{ event_type: "install", count: 500, success_rate: 99, avg_ms: 150 }];
    const { container } = render(
      <WebhookAnalyticsPanel total={1000} successRate={98.5} avgMs={200} p99Ms={800} eventTypes={eventTypes} />
    );
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("install");
  });
});
