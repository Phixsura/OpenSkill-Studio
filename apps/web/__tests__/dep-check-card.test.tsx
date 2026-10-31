import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepCheckCard } from "@/components/dep-check-card";

describe("DepCheckCard", () => {
  it("renders deps", () => {
    const { container } = render(
      <DepCheckCard allSatisfied={false} missingCount={1} dependencies={[
        { name: "auth", required: "1.0", installed: "1.5", status: "ok" },
        { name: "missing_dep", required: "*", installed: null, status: "missing" },
      ]} />
    );
    expect(container.textContent).toContain("Dependencies");
    expect(container.textContent).toContain("1 missing");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("v1.5");
    expect(container.textContent).toContain("not installed");
  });
});
