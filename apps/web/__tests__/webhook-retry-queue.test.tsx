import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookRetryQueue } from "@/components/webhook-retry-queue";

describe("WebhookRetryQueue", () => {
  it("renders queue", () => {
    const { container } = render(
      <WebhookRetryQueue deliveryRate={50} retrying={1} failed={1}
        entries={[
          { webhookId: "wh1", url: "https://a.com", attempts: 2, maxRetries: 5, status: "retrying" },
          { webhookId: "wh2", url: "https://b.com", attempts: 5, maxRetries: 5, status: "failed" },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Retries");
    expect(container.textContent).toContain("50% delivered");
    expect(container.textContent).toContain("1 retrying");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("wh1");
    expect(container.textContent).toContain("2/5");
  });
});
