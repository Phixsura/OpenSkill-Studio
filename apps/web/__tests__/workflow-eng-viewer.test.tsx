import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WorkflowEngViewer } from "@/components/workflow-eng-viewer";

describe("WorkflowEngViewer", () => {
  it("renders", () => {
    const { container } = render(
      <WorkflowEngViewer name="deploy" success={true}
        steps={[
          { step: "build", status: "success" },
          { step: "test", status: "success" },
          { step: "deploy", status: "success" },
        ]} />
    );
    expect(container.textContent).toContain("Workflow: deploy");
    expect(container.textContent).toContain("Complete");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("test");
    expect(container.textContent).toContain("deploy");
  });
});
