import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiffViewer } from "@/components/diff-viewer";

describe("DiffViewer", () => {
  it("renders diff", () => {
    const { container } = render(
      <DiffViewer added={2} removed={1} summary="+2 -1" lines={[
        { type: "unchanged", line: 1, content: "line1" },
        { type: "removed", line: 2, content: "old line" },
        { type: "added", line: 2, content: "new line" },
        { type: "added", line: 4, content: "extra line" },
      ]} />
    );
    expect(container.textContent).toContain("+2 -1");
    expect(container.textContent).toContain("line1");
    expect(container.textContent).toContain("old line");
    expect(container.textContent).toContain("new line");
    expect(container.textContent).toContain("extra line");
  });
});
