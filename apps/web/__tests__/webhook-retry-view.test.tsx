import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookRetryView } from "@/components/webhook-retry-view";

describe("WebhookRetryView", () => {
  const deliveries = [
    { attempt: 1, statusCode: 500, success: false, responseMs: 100, error: "Server error" },
    { attempt: 2, statusCode: 200, success: true, responseMs: 50, error: "" },
  ];
  it("renders delivery attempts", () => {
    const { container } = render(
      <WebhookRetryView deliveries={deliveries} status="delivered" totalAttempts={2} />
    );
    expect(container.textContent).toContain("Attempt 1");
    expect(container.textContent).toContain("Attempt 2");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("delivered");
  });
});
