import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookDebuggerPanel } from "@/components/webhook-debugger-panel";

describe("WebhookDebuggerPanel", () => {
  it("renders attempts", () => {
    const attempts = [
      { event_type: "app.installed", status_code: 200, success: true, response_time_ms: 50, timestamp: "" },
      { event_type: "app.updated", status_code: 500, success: false, response_time_ms: 200, timestamp: "" },
    ];
    const { container } = render(<WebhookDebuggerPanel attempts={attempts} onReplay={vi.fn()} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("500");
  });
  it("empty state", () => {
    const { container } = render(<WebhookDebuggerPanel attempts={[]} onReplay={vi.fn()} />);
    expect(container.textContent).toContain("No delivery attempts");
  });
  it("replay on failure", () => {
    const fn = vi.fn();
    const attempts = [{ event_type: "x", status_code: 500, success: false, response_time_ms: 100, timestamp: "" }];
    const { container } = render(<WebhookDebuggerPanel attempts={attempts} onReplay={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
