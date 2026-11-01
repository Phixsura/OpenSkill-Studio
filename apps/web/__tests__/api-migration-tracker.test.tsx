import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiMigrationTracker } from "@/components/api-migration-tracker";

describe("ApiMigrationTracker", () => {
  it("renders", () => {
    const { container } = render(
      <ApiMigrationTracker from="v1" to="v2" migrated={8} remaining={2}
        progressPct={80} deprecatedPaths={["/legacy", "/old"]} complete={false} />
    );
    expect(container.textContent).toContain("API Migration: v1 → v2");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("2 remaining");
    expect(container.textContent).toContain("/legacy");
  });
});
