import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RollbackPlanner } from "@/components/rollback-planner";

describe("RollbackPlanner", () => {
  it("renders", () => {
    const { container } = render(
      <RollbackPlanner currentVersion="2.1.0" targetVersion="2.0.0" risk="medium" estimatedMinutes={8}
        steps={[
          { action: "rollback_migrations", count: 1 },
          { action: "deploy_previous", version: "2.0.0" },
          { action: "verify_health", timeoutSeconds: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Rollback Plan");
    expect(container.textContent).toContain("medium risk");
    expect(container.textContent).toContain("2.1.0");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("~8min");
    expect(container.textContent).toContain("rollback_migrations");
    expect(container.textContent).toContain("verify_health");
  });
});
