import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepConflictViewer } from "@/components/dep-conflict-viewer";

const conflicts = [{
  package: "react",
  requirements: [
    { package: "react", constraint: "^16.0.0", requiredBy: "ext-a" },
    { package: "react", constraint: "^18.0.0", requiredBy: "ext-b" },
  ],
  reason: "No compatible version",
}];

const resolutions = [
  { package: "axios", version: "1.5.0", strategy: "newest" },
  { package: "react", version: "18.2.0", strategy: "force" },
];

describe("DepConflictViewer", () => {
  it("renders conflicts with requirement chains", () => {
    const { container } = render(<DepConflictViewer conflicts={conflicts} resolutions={[]} />);
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("^16.0.0");
    expect(container.textContent).toContain("ext-a");
    expect(container.textContent).toContain("Conflicts (1)");
  });

  it("renders resolutions with strategy badges", () => {
    const { container } = render(<DepConflictViewer conflicts={[]} resolutions={resolutions} />);
    expect(container.textContent).toContain("v1.5.0");
    expect(container.textContent).toContain("Newest Compatible");
    expect(container.textContent).toContain("Forced");
  });

  it("shows clean state when no conflicts", () => {
    const { container } = render(<DepConflictViewer conflicts={[]} resolutions={[]} />);
    expect(container.textContent).toContain("No dependency conflicts");
  });
});
