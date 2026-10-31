import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorPagePanel } from "@/components/error-page-panel";
describe("ErrorPagePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrorPagePanel total={50} mostCommon="NOT_FOUND"
        byCode={[
          { code: "NOT_FOUND", count: 30 },
          { code: "INTERNAL_ERROR", count: 15 },
          { code: "UNAUTHORIZED", count: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Error Summary");
    expect(container.textContent).toContain("50 errors");
    expect(container.textContent).toContain("most: NOT_FOUND");
    expect(container.textContent).toContain("NOT_FOUND");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("INTERNAL_ERROR");
  });
});
