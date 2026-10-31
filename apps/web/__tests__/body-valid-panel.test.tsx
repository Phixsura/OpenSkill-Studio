import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BodyValidPanel } from "@/components/body-valid-panel";

describe("BodyValidPanel", () => {
  it("renders", () => {
    const { container } = render(
      <BodyValidPanel valid={false} endpoint="POST /users"
        errors={[
          { field: "name", error: "minLength 1" },
          { field: "email", error: "required" },
        ]} />
    );
    expect(container.textContent).toContain("Body Validation");
    expect(container.textContent).toContain("2 errors");
    expect(container.textContent).toContain("POST /users");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("minLength 1");
  });
});
