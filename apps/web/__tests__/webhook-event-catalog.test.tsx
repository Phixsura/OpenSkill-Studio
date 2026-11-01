import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookEventCatalog } from "@/components/webhook-event-catalog";

describe("WebhookEventCatalog", () => {
  it("renders catalog", () => {
    const { container } = render(
      <WebhookEventCatalog selectedCategory={null} onSelectCategory={vi.fn()}
        categories={["lifecycle", "billing"]}
        events={[
          { type: "app.installed", category: "lifecycle", description: "App installed" },
          { type: "payment.completed", category: "billing", description: "Payment done" },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Events");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("App installed");
    expect(container.textContent).toContain("lifecycle");
    expect(container.textContent).toContain("billing");
  });
});
