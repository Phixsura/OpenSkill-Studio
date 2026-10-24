import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseGatePanel } from "@/components/release-gate-panel";
describe("ReleaseGatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReleaseGatePanel release="v2.0" canRelease={false} passedCount={1}
        gates={[
          { name: "tests", passed: true, required: true },
          { name: "security", passed: false, required: true },
          { name: "perf", passed: false, required: false },
        ]} />
    );
    expect(container.textContent).toContain("Release Gates: v2.0");
    expect(container.textContent).toContain("Blocked");
    expect(container.textContent).toContain("1/3");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("optional");
  });
});
