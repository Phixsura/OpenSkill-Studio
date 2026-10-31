import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorGroupList } from "@/components/error-group-list";

describe("ErrorGroupList", () => {
  it("renders groups", () => {
    const { container } = render(
      <ErrorGroupList uniqueErrors={2} totalOccurrences={5} dedupRatio={2.5}
        groups={[
          { fingerprint: "abc123", type: "TypeError", message: "null ref", count: 3 },
          { fingerprint: "def456", type: "SyntaxError", message: "unexpected", count: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Error Groups");
    expect(container.textContent).toContain("2 unique");
    expect(container.textContent).toContain("5 total");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("null ref");
    expect(container.textContent).toContain("abc123");
  });
});
