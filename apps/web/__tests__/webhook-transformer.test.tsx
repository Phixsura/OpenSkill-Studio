import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookTransformer } from "@/components/webhook-transformer";

describe("WebhookTransformer", () => {
  it("renders transformer", () => {
    const { container } = render(
      <WebhookTransformer templateJson='{"event":"{{ type }}"}' payloadJson='{"type":"install"}'
        outputJson='{"event":"install"}' placeholders={["type"]} />
    );
    expect(container.textContent).toContain("Payload Transformer");
    expect(container.textContent).toContain("Template");
    expect(container.textContent).toContain("Input");
    expect(container.textContent).toContain("Output");
    expect(container.textContent).toContain("{{ type }}");
  });
});
