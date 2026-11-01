import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RollbackManagerCard from "../src/components/rollback-manager-card";

const rollbacks = [
  {
    rollback_id: "rb1",
    from_version: "v2.0",
    to_version: "v1.0",
    reason: "Bug in v2.0",
    status: "completed" as const,
    initiated_by: "alice",
  },
  {
    rollback_id: "rb2",
    from_version: "v3.0",
    to_version: "v2.0",
    reason: "Performance",
    status: "in_progress" as const,
    initiated_by: "bob",
  },
];

describe("RollbackManagerCard", () => {
  it("renders header and current version", () => {
    const { container } = render(
      <RollbackManagerCard currentVersion="v1.0" rollbacks={rollbacks} appName="App" />,
    );
    expect(container.textContent).toContain("Rollback Manager");
    expect(container.textContent).toContain("v1.0");
  });

  it("shows version transitions", () => {
    const { container } = render(
      <RollbackManagerCard currentVersion="v1.0" rollbacks={rollbacks} appName="App" />,
    );
    expect(container.textContent).toContain("v2.0 → v1.0");
    expect(container.textContent).toContain("v3.0 → v2.0");
  });

  it("shows status badges", () => {
    const { container } = render(
      <RollbackManagerCard currentVersion="v1.0" rollbacks={rollbacks} appName="App" />,
    );
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("in progress");
  });

  it("shows reason and initiator", () => {
    const { container } = render(
      <RollbackManagerCard currentVersion="v1.0" rollbacks={rollbacks} appName="App" />,
    );
    expect(container.textContent).toContain("Bug in v2.0");
    expect(container.textContent).toContain("by alice");
  });

  it("shows empty state", () => {
    const { container } = render(
      <RollbackManagerCard currentVersion={null} rollbacks={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No rollbacks");
  });
});
