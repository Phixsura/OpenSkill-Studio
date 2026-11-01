import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyChecker } from "@/components/dependency-checker";

describe("DependencyChecker", () => {
  const packages = [
    { name: "next", current: "14.0.0", latest: "15.1.0", outdated: true, updateType: "major", breaking: true },
    { name: "lodash", current: "4.17.21", latest: "4.17.21", outdated: false, updateType: null, breaking: false },
  ];
  it("renders packages", () => {
    const { container } = render(
      <DependencyChecker packages={packages} outdated={1} majorUpdates={1} health="critical" />
    );
    expect(container.textContent).toContain("next");
    expect(container.textContent).toContain("14.0.0");
    expect(container.textContent).toContain("15.1.0");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("🚨");
  });
});
