import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiffViewer } from "@/components/diff-viewer";

describe("DiffViewer", () => {
  const hunks = [{
    header: "@@ -1,3 +1,4 @@",
    lines: [
      { content: " unchanged", type: "context" as const },
      { content: "-old line", type: "remove" as const },
      { content: "+new line", type: "add" as const },
    ],
  }];
  it("renders diff", () => {
    const { container } = render(<DiffViewer hunks={hunks} additions={1} removals={1} />);
    expect(container.textContent).toContain("+1");
    expect(container.textContent).toContain("-1");
    expect(container.textContent).toContain("unchanged");
    expect(container.textContent).toContain("-old line");
    expect(container.textContent).toContain("+new line");
  });
});
