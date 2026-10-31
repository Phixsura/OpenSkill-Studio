import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespValidPanel } from "@/components/resp-valid-panel";
describe("RespValidPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespValidPanel valid={false} fieldsChecked={3} validityPct={50}
        errors={[{ field: "id", error: "expected string" }, { field: "name", error: "required" }]} />
    );
    expect(container.textContent).toContain("Response Validator");
    expect(container.textContent).toContain("50% valid");
    expect(container.textContent).toContain("3 fields");
    expect(container.textContent).toContain("id");
    expect(container.textContent).toContain("expected string");
    expect(container.textContent).toContain("name");
  });
});
