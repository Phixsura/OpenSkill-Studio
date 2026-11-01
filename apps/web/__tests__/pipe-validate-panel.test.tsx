import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipeValidatePanel } from "@/components/pipe-validate-panel";
describe("PipeValidatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <PipeValidatePanel valid={false} stages={2} pipelineName="ci-cd"
        errors={[
          { field: "stages[1].name", error: "duplicate_name" },
          { field: "trigger", error: "invalid_trigger_type" },
        ]} />
    );
    expect(container.textContent).toContain("Pipeline Validator");
    expect(container.textContent).toContain("2 errors");
    expect(container.textContent).toContain("ci-cd");
    expect(container.textContent).toContain("duplicate_name");
    expect(container.textContent).toContain("invalid_trigger_type");
  });
});
