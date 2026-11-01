import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookPayloadInspector } from "@/components/webhook-payload-inspector";

describe("WebhookPayloadInspector", () => {
  it("renders payload", () => {
    const { container } = render(
      <WebhookPayloadInspector payload={{ event: "test", data: { key: "value" } }} sizeBytes={256} withinLimit={true} />
    );
    expect(container.textContent).toContain("event");
    expect(container.textContent).toContain("256B");
    expect(container.textContent).toContain("✅");
  });
  it("over limit", () => {
    const { container } = render(
      <WebhookPayloadInspector payload={{}} sizeBytes={300000} withinLimit={false} />
    );
    expect(container.textContent).toContain("Over limit");
  });
});
