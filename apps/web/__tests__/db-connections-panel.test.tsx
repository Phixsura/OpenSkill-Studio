import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DbConnectionsPanel } from "@/components/db-connections-panel";

const connections = [
  { connId: "db-1", dbType: "postgres", host: "localhost:5432", database: "myapp", status: "connected", poolSize: 10, activeQueries: 3, totalQueries: 1500 },
];

describe("DbConnectionsPanel", () => {
  it("renders connections", () => {
    const { container } = render(<DbConnectionsPanel connections={connections} />);
    expect(container.textContent).toContain("myapp");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("3/10 pool");
  });
  it("disconnect", () => {
    const fn = vi.fn();
    const { container } = render(<DbConnectionsPanel connections={connections} onDisconnect={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("db-1");
  });
});
