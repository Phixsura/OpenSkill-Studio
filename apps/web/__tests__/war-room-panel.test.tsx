import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WarRoomPanel } from "@/components/war-room-panel";

describe("WarRoomPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WarRoomPanel incidentId="INC-42" title="Database Outage" severity="critical"
        commander="alice" status="active" participants={["alice", "bob"]}
        onAddUpdate={vi.fn()}
        updates={[
          { author: "bob", message: "Investigating", seq: 1 },
          { author: "alice", message: "Root cause found", seq: 2 },
        ]} />
    );
    expect(container.textContent).toContain("War Room: Database Outage");
    expect(container.textContent).toContain("INC-42");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("Investigating");
    expect(container.textContent).toContain("Root cause found");
    expect(container.textContent).toContain("Add Update");
  });
});
