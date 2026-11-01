import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-webhook-transform-pipeline-card";

describe("ConsumerApiWebhookTransformPipelineCard", () => {
  it("shows pipelines", () => {
    const pipelines = [{ id: "p1", webhookId: "w1", steps: [{ id: "s1", type: "filter", order: 1, enabled: true }, { id: "s2", type: "redact", order: 2, enabled: true }] }];
    const { container } = render(<Card pipelines={pipelines} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Transform Pipelines");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("filter");
    expect(container.textContent).toContain("redact");
  });
  it("shows empty", () => {
    const { container } = render(<Card pipelines={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No pipelines");
  });
});
