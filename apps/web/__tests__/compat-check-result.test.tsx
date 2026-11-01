import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatCheckResult } from "@/components/compat-check-result";

describe("CompatCheckResult", () => {
  it("renders result", () => {
    const { container } = render(
      <CompatCheckResult compatible={false}
        breakingChanges={[{ type: "endpoint_removed", path: "/old" }]}
        compatibleChanges={[{ type: "endpoint_added", path: "/new" }]} />
    );
    expect(container.textContent).toContain("API Compatibility");
    expect(container.textContent).toContain("1 Breaking");
    expect(container.textContent).toContain("endpoint_removed");
    expect(container.textContent).toContain("/old");
    expect(container.textContent).toContain("endpoint_added");
    expect(container.textContent).toContain("/new");
  });
});
