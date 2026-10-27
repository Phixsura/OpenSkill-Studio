import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTestConsole } from "@/components/webhook-test-console";

const MOCK_HISTORY = [
  {
    test_id: "t1",
    event_type: "skill_pack.published",
    webhook_url: "https://app.com/hook",
    status: "pass" as const,
    status_code: 200,
    latency_ms: 45,
    response_body: null,
    error: null,
    timestamp: "2026-10-28T14:00:00Z",
  },
  {
    test_id: "t2",
    event_type: "app.installed",
    webhook_url: "https://app.com/hook",
    status: "fail" as const,
    status_code: 500,
    latency_ms: 120,
    response_body: null,
    error: null,
    timestamp: "2026-10-28T13:55:00Z",
  },
  {
    test_id: "t3",
    event_type: "submission.graded",
    webhook_url: "https://broken.com",
    status: "error" as const,
    status_code: null,
    latency_ms: null,
    response_body: null,
    error: "Connection refused",
    timestamp: "2026-10-28T13:50:00Z",
  },
];

const defaultProps = {
  templates: ["skill_pack.published", "app.installed", "submission.graded"],
  history: MOCK_HISTORY,
  passRate: 33.3,
  onSendTest: vi.fn(),
};

describe("WebhookTestConsole", () => {
  it("renders heading", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("Webhook Test Console");
  });

  it("renders pass rate", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("33.3% pass rate");
  });

  it("renders event type selector", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    const select = container.querySelector("select[aria-label='Event type']");
    expect(select).toBeTruthy();
  });

  it("renders URL input", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    const input = container.querySelector("input[aria-label='Webhook URL']");
    expect(input).toBeTruthy();
  });

  it("calls onSendTest with event type and URL", () => {
    const onSendTest = vi.fn();
    const { container } = render(<WebhookTestConsole {...defaultProps} onSendTest={onSendTest} />);
    const input = container.querySelector("input[aria-label='Webhook URL']") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "https://test.com/hook" } });
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Send Test",
    );
    fireEvent.click(btn!);
    expect(onSendTest).toHaveBeenCalledWith("skill_pack.published", "https://test.com/hook");
  });

  it("disables Send when URL empty", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Send Test",
    ) as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });

  it("renders status badges", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("Pass");
    expect(container.textContent).toContain("Fail");
    expect(container.textContent).toContain("Error");
  });

  it("renders event types in history", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("skill_pack.published");
    expect(container.textContent).toContain("app.installed");
  });

  it("renders HTTP status codes", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("HTTP 200");
    expect(container.textContent).toContain("HTTP 500");
  });

  it("renders latency", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("45ms");
  });

  it("renders error message", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} />);
    expect(container.textContent).toContain("Connection refused");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookTestConsole {...defaultProps} history={[]} />);
    expect(container.textContent).toContain("No tests yet");
  });
});
