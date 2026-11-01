import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookStatus } from "@/components/webhook-status";

const DELIVERIES = [
  { id: "1", event_type: "submission.completed", url: "https://x.com/hook", status: "delivered" as const, http_status: 200, attempt: 1, duration_ms: 150, created_at: "2026-01-01" },
  { id: "2", event_type: "app.installed", url: "https://x.com/hook", status: "failed" as const, http_status: 500, attempt: 3, duration_ms: 5000, created_at: "2026-01-01" },
];

describe("WebhookStatus", () => {
  it("renders deliveries", () => {
    const { container } = render(<WebhookStatus deliveries={DELIVERIES} />);
    expect(container.textContent).toContain("submission.completed");
    expect(container.textContent).toContain("app.installed");
  });

  it("shows status badges", () => {
    const { container } = render(<WebhookStatus deliveries={DELIVERIES} />);
    expect(container.textContent).toContain("Delivered");
    expect(container.textContent).toContain("Failed");
  });

  it("shows HTTP status", () => {
    const { container } = render(<WebhookStatus deliveries={DELIVERIES} />);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookStatus deliveries={[]} />);
    expect(container.textContent).toContain("No webhook");
  });

  it("shows duration", () => {
    const { container } = render(<WebhookStatus deliveries={DELIVERIES} />);
    expect(container.textContent).toContain("150ms");
  });
});
