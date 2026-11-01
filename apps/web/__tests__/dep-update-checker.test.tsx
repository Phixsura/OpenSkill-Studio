import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DepUpdateChecker } from "@/components/dep-update-checker";

describe("DepUpdateChecker", () => {
  it("renders updates", () => {
    const { container } = render(
      <DepUpdateChecker upToDate={5} total={7} hasMajor={true} onUpdate={vi.fn()}
        outdated={[
          { name: "react", current: "18.2.0", latest: "19.0.0", type: "major", breaking: true },
          { name: "axios", current: "1.5.0", latest: "1.6.0", type: "minor", breaking: false },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Updates");
    expect(container.textContent).toContain("5 current");
    expect(container.textContent).toContain("2 outdated");
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("18.2.0 → 19.0.0");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("Update");
  });
});
