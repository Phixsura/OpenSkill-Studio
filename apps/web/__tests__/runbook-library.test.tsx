import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RunbookLibrary } from "@/components/runbook-library";

describe("RunbookLibrary", () => {
  it("renders library", () => {
    const { container } = render(
      <RunbookLibrary total={5} categories={["infrastructure", "deployment"]} onSelect={vi.fn()}
        runbooks={[
          { slug: "db-failover", title: "Database Failover", category: "infrastructure", stepCount: 5, tags: ["database"], uses: 12 },
          { slug: "deploy-rollback", title: "Deployment Rollback", category: "deployment", stepCount: 3, tags: ["deploy"], uses: 8 },
        ]} />
    );
    expect(container.textContent).toContain("Runbook Library");
    expect(container.textContent).toContain("5 runbooks");
    expect(container.textContent).toContain("Database Failover");
    expect(container.textContent).toContain("5 steps");
    expect(container.textContent).toContain("12 uses");
    expect(container.textContent).toContain("infrastructure");
  });
});
