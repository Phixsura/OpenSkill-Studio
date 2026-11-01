import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookConfigPage } from "@/components/webhook-config-page";

describe("WebhookConfigPage", () => {
  const webhooks = [
    { id: "wh1", url: "https://a.com/hook", events: ["app.installed"], eventCount: 1, active: true, successRate: 98.5 },
  ];
  it("renders config page", () => {
    const { container } = render(
      <WebhookConfigPage webhooks={webhooks} active={1} canAdd={true} totalEventTypes={9}
        onAdd={vi.fn()} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("https://a.com/hook");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("+ Add Webhook");
  });
  it("empty state", () => {
    const { container } = render(
      <WebhookConfigPage webhooks={[]} active={0} canAdd={true} totalEventTypes={9}
        onAdd={vi.fn()} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("No webhooks configured");
    expect(container.textContent).toContain("Create First Webhook");
  });
});
