import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookPayloadPreview } from "@/components/webhook-payload-preview";

describe("WebhookPayloadPreview", () => {
  it("renders payload", () => {
    const payload = { id: "evt_abc", type: "app.installed", action: "install" };
    const { container } = render(
      <WebhookPayloadPreview payload={payload} eventType="app.installed" valid={true} />
    );
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("evt_abc");
    expect(container.textContent).toContain("Valid");
  });
});
