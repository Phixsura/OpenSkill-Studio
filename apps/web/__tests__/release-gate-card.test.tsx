import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseGateCard } from "@/components/release-gate-card";

describe("ReleaseGateCard", () => {
  it("renders gate", () => {
    const { container } = render(
      <ReleaseGateCard name="v2.0" canRelease={false} passed={1} failed={1} total={2}
        checks={[
          { name: "tests", type: "required", status: "passed" },
          { name: "security", type: "required", status: "failed" },
        ]} />
    );
    expect(container.textContent).toContain("Release Gate: v2.0");
    expect(container.textContent).toContain("Blocked");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("security");
  });
});
