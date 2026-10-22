import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ManifestLintResults } from "@/components/manifest-lint-results";

describe("ManifestLintResults", () => {
  it("shows clean state", () => {
    const { container } = render(<ManifestLintResults results={[]} />);
    expect(container.textContent).toContain("looks great");
  });

  it("shows suggestions", () => {
    const results = [{ level: "warning", field: "app.description", message: "Add description" }];
    const { container } = render(<ManifestLintResults results={results} />);
    expect(container.textContent).toContain("Add description");
    expect(container.textContent).toContain("⚠️");
  });

  it("shows count", () => {
    const results = [
      { level: "info", field: "a", message: "x" },
      { level: "info", field: "b", message: "y" },
    ];
    const { container } = render(<ManifestLintResults results={results} />);
    expect(container.textContent).toContain("2 suggestions");
  });
});
