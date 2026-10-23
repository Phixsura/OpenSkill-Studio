import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookLog } from "@/components/webhook-log";

describe("WebhookLog", () => {
  const deliveries = [
    { id: "1", event: "app.installed", url: "https://example.com/hook", status_code: 200, success: true, duration_ms: 150, timestamp: "2026-01-02", attempt: 1 },
    { id: "2", event: "app.updated", url: "https://example.com/hook", status_code: 500, success: false, duration_ms: 3000, timestamp: "2026-01-01", attempt: 1 },
  ];
  it("renders deliveries", () => {
    const { container } = render(<WebhookLog deliveries={deliveries} successRate={50} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50%");
  });
});
