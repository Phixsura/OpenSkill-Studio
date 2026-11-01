import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TextDiffView } from "@/components/text-diff-view";

describe("TextDiffView", () => {
  it("shows changes", () => {
    const { container } = render(
      <TextDiffView added={["red", "jumps"]} removed={["brown"]} addedCount={2} removedCount={1} similarityPct={75} hasChanges={true} />
    );
    expect(container.textContent).toContain("+2 added");
    expect(container.textContent).toContain("-1 removed");
    expect(container.textContent).toContain("red");
    expect(container.textContent).toContain("brown");
  });
  it("no changes", () => {
    const { container } = render(
      <TextDiffView added={[]} removed={[]} addedCount={0} removedCount={0} similarityPct={100} hasChanges={false} />
    );
    expect(container.textContent).toContain("No changes");
  });
});
