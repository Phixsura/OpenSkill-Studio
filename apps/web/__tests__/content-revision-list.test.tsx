import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContentRevisionList } from "@/components/content-revision-list";

describe("ContentRevisionList", () => {
  it("renders revisions", () => {
    const { container } = render(
      <ContentRevisionList total={3} authorCount={2} onRestore={vi.fn()}
        revisions={[
          { revision: "abc1234567", author: "alice", message: "Latest update", size: 500 },
          { revision: "def7890123", author: "bob", message: "Initial", size: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Revisions");
    expect(container.textContent).toContain("3 revisions");
    expect(container.textContent).toContain("2 authors");
    expect(container.textContent).toContain("abc1234567");
    expect(container.textContent).toContain("latest");
    expect(container.textContent).toContain("Restore");
  });
});
