import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookInterceptorPanel } from "@/components/webhook-interceptor-panel";

const mockCaptures = [
  { interceptId: "i1", direction: "outbound" as const, url: "https://api.example.com/hook",
    method: "POST", body: '{"event":"deploy"}', statusCode: 200,
    paused: false, modified: false, timestamp: "12:00" },
  { interceptId: "i2", direction: "inbound" as const, url: "https://myext.com/webhook",
    method: "POST", body: '{"action":"push"}', statusCode: 0,
    paused: true, modified: false, timestamp: "12:05" },
];

describe("WebhookInterceptorPanel", () => {
  it("renders captures", () => {
    const { container } = render(
      <WebhookInterceptorPanel captures={mockCaptures} pausedCount={1} />
    );
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("1 paused");
  });

  it("shows paused indicator", () => {
    const { container } = render(
      <WebhookInterceptorPanel captures={mockCaptures} pausedCount={1} />
    );
    expect(container.textContent).toContain("PAUSED");
  });

  it("calls onResume", () => {
    const onResume = vi.fn();
    const { getByText } = render(
      <WebhookInterceptorPanel captures={mockCaptures} pausedCount={1} onResume={onResume} />
    );
    fireEvent.click(getByText("Resume"));
    expect(onResume).toHaveBeenCalledWith("i2");
  });

  it("filters by direction", () => {
    const { getByText, container } = render(
      <WebhookInterceptorPanel captures={mockCaptures} pausedCount={0} />
    );
    fireEvent.click(getByText("inbound"));
    expect(container.textContent).toContain("myext.com");
    expect(container.textContent).not.toContain("api.example.com");
  });
});
