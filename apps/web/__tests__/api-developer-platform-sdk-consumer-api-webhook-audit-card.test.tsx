import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookAuditCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-audit-card";

describe("WebhookAuditCard", () => {
  it("renders title and entries", () => {
    const { container } = render(<WebhookAuditCard />);
    expect(container.textContent).toContain("Webhook Audit Log");
    expect(container.textContent).toContain("wh-orders");
    expect(container.textContent).toContain("secret_rotated");
  });

  it("shows count", () => {
    const { container } = render(<WebhookAuditCard />);
    expect(container.textContent).toContain("4 audit entries");
  });
});
