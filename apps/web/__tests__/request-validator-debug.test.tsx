import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestValidatorDebug } from "@/components/request-validator-debug";

describe("RequestValidatorDebug", () => {
  it("valid", () => {
    const { container } = render(
      <RequestValidatorDebug valid={true} errors={[]} method="GET" path="/api/apps" />
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("✅ Valid");
  });
  it("errors", () => {
    const errors = [{ field: "Authorization", error: "Required" }];
    const { container } = render(
      <RequestValidatorDebug valid={false} errors={errors} method="POST" path="/api/apps" />
    );
    expect(container.textContent).toContain("❌ 1 errors");
    expect(container.textContent).toContain("Authorization");
    expect(container.textContent).toContain("Required");
  });
});
