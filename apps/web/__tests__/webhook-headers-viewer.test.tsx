import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookHeadersViewer } from "@/components/webhook-headers-viewer";

describe("WebhookHeadersViewer", () => {
  it("renders headers", () => {
    const { container } = render(
      <WebhookHeadersViewer verified={true} headers={{
        "X-Webhook-Event": "app.installed",
        "Content-Type": "application/json",
      }} />
    );
    expect(container.textContent).toContain("Request Headers");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("X-Webhook-Event");
    expect(container.textContent).toContain("app.installed");
  });
});
