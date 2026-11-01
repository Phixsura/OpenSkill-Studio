import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookConfigPanel } from "@/components/webhook-config-panel";

describe("WebhookConfigPanel", () => {
  it("renders config", () => {
    const onEdit = vi.fn();
    const { container, getAllByText } = render(
      <WebhookConfigPanel activeCount={1} allSecure={true} onAdd={vi.fn()} onToggle={vi.fn()} onEdit={onEdit}
        webhooks={[
          { id: "wh1", url: "https://example.com/hook", eventCount: 2, active: true, secure: true, lastDelivery: "5m ago", successRate: 98.5 },
        ]} />
    );
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("https://example.com/hook");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("98.5%");
    fireEvent.click(getAllByText("Edit")[0]);
    expect(onEdit).toHaveBeenCalledWith("wh1");
  });
});
