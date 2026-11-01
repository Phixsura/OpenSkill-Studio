import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-webhook-transform-pipeline-card";

describe("TransformPipelineCard", () => {
  it("shows pipelines", () => {
    const pipelines = [{ pipeline_id: "p1", consumer_id: "c1", steps: [{ step_id: "s1", transform_type: "add_field" }, { step_id: "s2", transform_type: "remove_field" }], executions: 500 }];
    const { container } = render(<Card pipelines={pipelines} appName="App" />);
    expect(container.textContent).toContain("Transform Pipelines");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("add_field");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<Card pipelines={[]} appName="App" />);
    expect(container.textContent).toContain("No pipelines configured");
  });
});
