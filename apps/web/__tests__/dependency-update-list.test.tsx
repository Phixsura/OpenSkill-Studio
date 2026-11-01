import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DependencyUpdateList } from "@/components/dependency-update-list";

describe("DependencyUpdateList", () => {
  const deps = [
    { name: "next", current: "14.0.0", latest: "15.0.0", needsUpdate: true, updateType: "major", isBreaking: true },
    { name: "lodash", current: "4.17.21", latest: "4.17.21", needsUpdate: false, updateType: null, isBreaking: false },
  ];
  it("renders deps", () => {
    const { container } = render(
      <DependencyUpdateList dependencies={deps} updatesAvailable={1} breaking={1} onUpdateAll={vi.fn()} />
    );
    expect(container.textContent).toContain("next");
    expect(container.textContent).toContain("14.0.0");
    expect(container.textContent).toContain("15.0.0");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("Update All");
  });
});
