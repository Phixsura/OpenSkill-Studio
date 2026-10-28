import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RollbackManagerCard from "../src/components/rollback-manager-card";

const rollbacks = [
  {
    rollback_id: "rb-1",
    from_version: "2.0.0",
    to_version: "1.9.0",
    reason: "Critical bug in payments",
    status: "completed" as const,
    initiated_by: "ops-team",
    created_at: new Date(Date.now() - 3_600_000).toISOString(),
  },
  {
    rollback_id: "rb-2",
    from_version: "2.1.0",
    to_version: "2.0.0",
    reason: "Performance regression",
    status: "in_progress" as const,
    initiated_by: "admin",
    created_at: new Date(Date.now() - 300_000).toISOString(),
  },
];

describe("RollbackManagerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="My App" />);
    expect(container.textContent).toContain("Rollbacks");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="App" />);
    expect(container.textContent).toContain("1 active");
  });

  it("renders version transition", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="App" />);
    expect(container.textContent).toContain("2.0.0 → 1.9.0");
  });

  it("shows reason", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="App" />);
    expect(container.textContent).toContain("Critical bug in payments");
  });

  it("shows initiator", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="App" />);
    expect(container.textContent).toContain("ops-team");
  });

  it("shows status", () => {
    const { container } = render(<RollbackManagerCard rollbacks={rollbacks} appName="App" />);
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("in progress");
  });

  it("shows empty state", () => {
    const { container } = render(<RollbackManagerCard rollbacks={[]} appName="App" />);
    expect(container.textContent).toContain("No rollbacks");
  });
});
