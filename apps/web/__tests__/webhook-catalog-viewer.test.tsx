import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookCatalogViewer } from "@/components/webhook-catalog-viewer";

describe("WebhookCatalogViewer", () => {
  it("renders events", () => {
    const onSelect = vi.fn();
    const { container } = render(
      <WebhookCatalogViewer selectedCategory={null} onSelectCategory={onSelect}
        categories={["apps", "billing"]}
        events={[
          { type: "app.installed", description: "App installed", category: "apps", fields: ["app_id", "user_id"] },
          { type: "payment.completed", description: "Payment done", category: "billing", fields: ["payment_id"] },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Events");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("payment.completed");
    expect(container.textContent).toContain("app_id");
    const billingBtns = container.querySelectorAll("button"); fireEvent.click(billingBtns[2]);
    expect(onSelect).toHaveBeenCalledWith("billing");
  });
});
