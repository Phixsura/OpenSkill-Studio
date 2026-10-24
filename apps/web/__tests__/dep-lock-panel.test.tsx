import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepLockPanel } from "@/components/dep-lock-panel";
describe("DepLockPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepLockPanel locks={[
        { service: "api", version: "2.0.0", lockedBy: "release-mgr" },
        { service: "db", version: "14.2", lockedBy: "dba" },
      ]} />
    );
    expect(container.textContent).toContain("Dependency Locks");
    expect(container.textContent).toContain("2 locked");
    expect(container.textContent).toContain("api@2.0.0");
    expect(container.textContent).toContain("by release-mgr");
  });
});
