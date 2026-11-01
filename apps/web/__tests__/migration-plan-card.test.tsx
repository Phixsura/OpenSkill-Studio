import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MigrationPlanCard } from "@/components/migration-plan-card";

describe("MigrationPlanCard", () => {
  it("renders plan", () => {
    const { container } = render(
      <MigrationPlanCard current="1.0" target="2.0" risk="high" requiresDowntime={true} estimatedSec={15}
        steps={[
          { action: "add_column", table: "users", description: "Add email", estimatedSec: 5, breaking: false },
          { action: "drop_column", table: "users", description: "Drop legacy", estimatedSec: 10, breaking: true },
        ]} />
    );
    expect(container.textContent).toContain("Migration Plan");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("high risk");
    expect(container.textContent).toContain("downtime required");
    expect(container.textContent).toContain("add_column");
  });
});
