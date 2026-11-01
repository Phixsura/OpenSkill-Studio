import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DIContainerPanel } from "@/components/di-container-panel";

const mockServices = [
  { name: "db", implementation: "PostgresDB", lifetime: "singleton" as const, deps: [] },
  { name: "repo", implementation: "UserRepo", lifetime: "transient" as const, deps: ["db"] },
  { name: "auth", implementation: "AuthService", lifetime: "scoped" as const, deps: ["repo"] },
];
const mockGraph = { db: [], repo: ["db"], auth: ["repo"] };

describe("DIContainerPanel", () => {
  it("renders services", () => {
    const { container } = render(
      <DIContainerPanel services={mockServices} graph={mockGraph} />
    );
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("PostgresDB");
    expect(container.textContent).toContain("Singleton");
    expect(container.textContent).toContain("3 services");
  });

  it("shows dependency graph", () => {
    const { getByText, container } = render(
      <DIContainerPanel services={mockServices} graph={mockGraph} />
    );
    fireEvent.click(getByText("Dependency Graph"));
    expect(container.textContent).toContain("repo ← db");
    expect(container.textContent).toContain("db (no deps)");
  });

  it("calls onResolve", () => {
    const onResolve = vi.fn();
    const { getAllByText } = render(
      <DIContainerPanel services={mockServices} graph={mockGraph} onResolve={onResolve} />
    );
    fireEvent.click(getAllByText("Resolve")[0]);
    expect(onResolve).toHaveBeenCalledWith("db");
  });

  it("shows deps on service card", () => {
    const { container } = render(
      <DIContainerPanel services={mockServices} graph={mockGraph} />
    );
    expect(container.textContent).toContain("deps: db");
  });
});
