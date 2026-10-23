import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDeliveryLog } from "@/components/webhook-delivery-log";

describe("WebhookDeliveryLog", () => {
  it("renders log", () => {
    const { container } = render(
      <WebhookDeliveryLog totalDeliveries={3} successRate={66.7} avgDurationMs={120}
        entries={[
          { id: "d1", eventType: "app.installed", statusCode: 200, durationMs: 150, success: true, url: "" },
          { id: "d2", eventType: "app.updated", statusCode: 500, durationMs: 3000, success: false, url: "" },
        ]} />
    );
    expect(container.textContent).toContain("Delivery Log");
    expect(container.textContent).toContain("3 total");
    expect(container.textContent).toContain("66.7% success");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
