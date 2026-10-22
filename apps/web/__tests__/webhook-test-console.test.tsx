import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTestConsole } from "@/components/webhook-test-console";

describe("WebhookTestConsole", () => {
  it("shows event buttons", () => {
    const { container } = render(<WebhookTestConsole lastResult={null} onTest={vi.fn()} eventTypes={["app.installed", "submission.completed"]} />);
    expect(container.textContent).toContain("app.installed");
  });
  it("shows result", () => {
    const { container } = render(<WebhookTestConsole lastResult={{ statusCode: 200, durationMs: 150, success: true }} onTest={vi.fn()} eventTypes={[]} />);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("150ms");
  });
  it("no result initially", () => {
    const { container } = render(<WebhookTestConsole lastResult={null} onTest={vi.fn()} eventTypes={[]} />);
    expect(container.textContent).not.toContain("HTTP");
  });
});
