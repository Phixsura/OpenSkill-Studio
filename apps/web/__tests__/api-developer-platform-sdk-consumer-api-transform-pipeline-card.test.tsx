import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TransformPipelineCard from "../src/components/api-developer-platform-sdk-consumer-api-transform-pipeline-card";

describe("TransformPipelineCard", () => {
  it("renders title and steps", () => {
    const { container } = render(<TransformPipelineCard />);
    expect(container.textContent).toContain("Transform Pipeline");
    expect(container.textContent).toContain("Rename user_id");
    expect(container.textContent).toContain("Remove internal");
  });

  it("shows kinds and active count", () => {
    const { container } = render(<TransformPipelineCard />);
    expect(container.textContent).toContain("rename_field");
    expect(container.textContent).toContain("add_field");
    expect(container.textContent).toContain("3/4 steps active");
  });
});
