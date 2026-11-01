import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookTransformationPipelineCard from "../src/components/api-developer-api-webhook-transformation-pipeline-card";

const pipelines = [
  { pipeline_id: "normalize", steps: [{ step_id: "s1", operation: "rename_field" }, { step_id: "s2", operation: "remove_field" }], execution_count: 500, error_count: 2 },
];

describe("APIDeveloperAPIWebhookTransformationPipelineCard", () => {
  it("shows pipelines", () => {
    const { container } = render(<APIDeveloperAPIWebhookTransformationPipelineCard pipelines={pipelines} appName="App" />);
    expect(container.textContent).toContain("Transform Pipelines");
    expect(container.textContent).toContain("normalize");
    expect(container.textContent).toContain("500 runs");
    expect(container.textContent).toContain("rename_field");
    expect(container.textContent).toContain("2 errors");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookTransformationPipelineCard pipelines={[]} appName="App" />);
    expect(container.textContent).toContain("No pipelines");
  });
});
