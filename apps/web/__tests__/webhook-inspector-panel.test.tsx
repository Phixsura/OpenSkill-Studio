import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookInspectorPanel } from "@/components/webhook-inspector-panel";

describe("WebhookInspectorPanel", () => {
  it("renders inspector", () => {
    const { container } = render(
      <WebhookInspectorPanel headers={{ "content-type": "application/json" }}
        bodyRaw='{"event":"test"}' bodyParsed={{ event: "test" }} isJson={true}
        statusCode={200} success={true} durationMs={85} bodySizeBytes={18} />
    );
    expect(container.textContent).toContain("Webhook Inspector");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("content-type");
    expect(container.textContent).toContain("event");
  });
});
