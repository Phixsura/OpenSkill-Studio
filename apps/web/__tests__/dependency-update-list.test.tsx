import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DependencyUpdateList } from "@/components/dependency-update-list";

describe("DependencyUpdateList", () => {
  const updates = [
    { name: "react", current: "18.2.0", latest: "18.3.0", type: "minor", breaking: false },
    { name: "next", current: "14.0.0", latest: "15.1.0", type: "major", breaking: true },
  ];
  it("renders", () => {
    const { container } = render(
      <DependencyUpdateList updates={updates} totalDeps={3} breakingCount={1}
        onUpdateAll={vi.fn()} onUpdate={vi.fn()} />
    );
    expect(container.textContent).toContain("Dependency Updates");
    expect(container.textContent).toContain("2/3 outdated");
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("18.2.0 → 18.3.0");
    expect(container.textContent).toContain("major");
  });
  it("update single", () => {
    const fn = vi.fn();
    const { container } = render(
      <DependencyUpdateList updates={updates} totalDeps={3} breakingCount={1}
        onUpdateAll={vi.fn()} onUpdate={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Update")!);
    expect(fn).toHaveBeenCalledWith("react");
  });
});
