import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HeaderValidPanel } from "@/components/header-valid-panel";
describe("HeaderValidPanel", () => {
  it("renders errors", () => {
    const { container } = render(
      <HeaderValidPanel valid={false} headersChecked={2} totalSizeBytes={150}
        errors={[{ header: "Authorization", error: "missing_required" }]} />
    );
    expect(container.textContent).toContain("Header Validation");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("Authorization");
    expect(container.textContent).toContain("missing_required");
  });
});
