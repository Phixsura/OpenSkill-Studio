import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqValidatorPanel } from "@/components/req-validator-panel";

describe("ReqValidatorPanel", () => {
  it("renders errors", () => {
    const { container } = render(
      <ReqValidatorPanel valid={false} endpoint="POST /api/users"
        errors={[
          { field: "name", error: "min length 1" },
          { field: "email", error: "pattern mismatch" },
        ]} />
    );
    expect(container.textContent).toContain("Request Validator");
    expect(container.textContent).toContain("2 errors");
    expect(container.textContent).toContain("POST /api/users");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("min length 1");
  });
});
