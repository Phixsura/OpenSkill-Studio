import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookRoutingTable } from "@/components/webhook-routing-table";

describe("WebhookRoutingTable", () => {
  it("renders routes", () => {
    const routes = [{ event_type: "app.installed", endpoint_url: "https://x.com/hook", priority: 10, active: true }];
    const { container } = render(<WebhookRoutingTable routes={routes} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("ON");
  });
  it("empty state", () => {
    const { container } = render(<WebhookRoutingTable routes={[]} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("No routing rules");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const routes = [{ event_type: "x", endpoint_url: "y", priority: 0, active: true }];
    const { container } = render(<WebhookRoutingTable routes={routes} onToggle={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
