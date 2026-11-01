import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocsLintReport } from "@/components/docs-lint-report";

describe("DocsLintReport", () => {
  it("renders report", () => {
    const { container } = render(
      <DocsLintReport docScore={75} totalIssues={5} totalErrors={2}
        results={[
          { path: "/users", method: "GET", issueCount: 0, errors: 0, warnings: 0, valid: true },
          { path: "/orders", method: "POST", issueCount: 3, errors: 2, warnings: 1, valid: false },
        ]} />
    );
    expect(container.textContent).toContain("Docs Lint");
    expect(container.textContent).toContain("75% score");
    expect(container.textContent).toContain("5 issues");
    expect(container.textContent).toContain("2 errors");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("POST /orders");
  });
});
