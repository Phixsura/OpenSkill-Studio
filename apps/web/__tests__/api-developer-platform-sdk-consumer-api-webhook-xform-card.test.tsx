import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookTransformerCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-xform-card";

describe("WebhookTransformerCard", () => {
  it("renders title and pipelines", () => {
    const { container } = render(<WebhookTransformerCard />);
    expect(container.textContent).toContain("Webhook Transformer");
    expect(container.textContent).toContain("p-orders");
    expect(container.textContent).toContain("p-users");
  });

  it("shows ops and count", () => {
    const { container } = render(<WebhookTransformerCard />);
    expect(container.textContent).toContain("rename");
    expect(container.textContent).toContain("flatten");
    expect(container.textContent).toContain("2 pipelines");
  });
});
