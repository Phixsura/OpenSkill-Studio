import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookFilterEditor } from "@/components/webhook-filter-editor";

describe("WebhookFilterEditor", () => {
  it("renders filters", () => {
    const onToggle = vi.fn();
    const { container, getByText } = render(
      <WebhookFilterEditor dropRate={25} onToggle={onToggle}
        eventTypes={["app.installed", "app.uninstalled", "user.created"]}
        selectedTypes={["app.installed"]} />
    );
    expect(container.textContent).toContain("Webhook Filters");
    expect(container.textContent).toContain("25% filtered out");
    expect(container.textContent).toContain("app.installed");
    fireEvent.click(getByText("user.created"));
    expect(onToggle).toHaveBeenCalledWith("user.created");
  });
});
