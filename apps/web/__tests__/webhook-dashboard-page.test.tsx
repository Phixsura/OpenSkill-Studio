import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDashboardPage } from "@/components/webhook-dashboard-page";

describe("WebhookDashboardPage", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <WebhookDashboardPage endpoints={[{ url: "https://a.com/hook", active: true, events: [] }]}
        activeEndpoints={1} deliveries={{ total: 100, success: 95, failed: 5, successRate: 95 }}
        health="good" period="24h" />
    );
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("Healthy");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("95%");
  });
});
