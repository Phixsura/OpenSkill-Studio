import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookEventCatalogBrowser } from "@/components/webhook-event-catalog-browser";

describe("WebhookEventCatalogBrowser", () => {
  const categories = [{
    category: "app", label: "App Events",
    events: [{ event: "app.installed", description: "App installed", payload_example: {} }],
  }];
  it("renders", () => {
    const { container } = render(
      <WebhookEventCatalogBrowser categories={categories} totalEvents={1} onSubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Events");
    expect(container.textContent).toContain("App Events");
    expect(container.textContent).toContain("app.installed");
  });
  it("subscribe", () => {
    const fn = vi.fn();
    const { container } = render(
      <WebhookEventCatalogBrowser categories={categories} totalEvents={1} onSubscribe={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Subscribe")!);
    expect(fn).toHaveBeenCalledWith("app.installed");
  });
});
