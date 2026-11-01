import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueryComplexityBadge } from "@/components/query-complexity-badge";

describe("QueryComplexityBadge", () => {
  it("renders complexity", () => {
    const { container } = render(
      <QueryComplexityBadge complexity={45} maxComplexity={1000} depth={3}
        maxDepth={10} allowed={true} fields={15} lists={3} />
    );
    expect(container.textContent).toContain("Query Complexity");
    expect(container.textContent).toContain("Allowed");
    expect(container.textContent).toContain("45/1000");
    expect(container.textContent).toContain("3/10");
    expect(container.textContent).toContain("15 fields");
  });
});
