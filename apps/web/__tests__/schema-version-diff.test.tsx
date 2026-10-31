import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SchemaVersionDiff } from "@/components/schema-version-diff";

describe("SchemaVersionDiff", () => {
  it("renders breaking changes", () => {
    const { container } = render(
      <SchemaVersionDiff breaking={true} suggestedBump="major"
        added={["email"]} removed={["age"]}
        changed={[{ field: "name", old: "string", new: "text" }]} />
    );
    expect(container.textContent).toContain("Schema Diff");
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("+ email");
    expect(container.textContent).toContain("- age");
  });
});
