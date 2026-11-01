import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncLearningCard } from "@/components/inc-learning-card";

describe("IncLearningCard", () => {
  it("renders", () => {
    const { container } = render(
      <IncLearningCard incidentId="INC-1" lessonCount={2} byArea={{ detection: 1, response: 1 }}
        lessons={[
          { area: "detection", lesson: "Add better monitoring", priority: "high" },
          { area: "response", lesson: "Create runbook", priority: "medium" },
        ]} />
    );
    expect(container.textContent).toContain("Learnings: INC-1");
    expect(container.textContent).toContain("2 lessons");
    expect(container.textContent).toContain("Add better monitoring");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("detection");
  });
});
