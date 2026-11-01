import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhooksPage } from "@/components/webhooks-page";

describe("WebhooksPage", () => {
  const webhooks = [{ id: "wh1", url: "https://a.com/hook", events: ["app.installed"], active: true, successRate: 98 }];
  const stats = { total: 100, success: 95, failed: 5, successRate: 95 };
  it("renders webhooks page", () => {
    const { container } = render(
      <WebhooksPage appName="SuperApp" webhooks={webhooks} active={1}
        deliveryStats={stats} health="good"
        onAdd={vi.fn()} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp — Webhooks");
    expect(container.textContent).toContain("https://a.com/hook");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("+ Add Webhook");
  });
});
