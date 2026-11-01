import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SchemaDiffViewer } from "@/components/schema-diff-viewer";

describe("SchemaDiffViewer", () => {
  it("renders", () => {
    const { container } = render(
      <SchemaDiffViewer added={["avatar", "role"]} removed={["email"]}
        unchanged={["id", "name"]} breaking={true} totalChanges={3} />
    );
    expect(container.textContent).toContain("Schema Diff");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ avatar");
    expect(container.textContent).toContain("- email");
    expect(container.textContent).toContain("id");
  });
});
