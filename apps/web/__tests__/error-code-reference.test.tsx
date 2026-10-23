import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorCodeReference } from "@/components/error-code-reference";

describe("ErrorCodeReference", () => {
  it("renders codes", () => {
    const { container } = render(
      <ErrorCodeReference categories={["auth", "api"]} codes={[
        { code: "AUTH_001", message: "Invalid credentials", status: 401, category: "auth" },
        { code: "API_001", message: "Rate limit exceeded", status: 429, category: "api" },
      ]} />
    );
    expect(container.textContent).toContain("Error Codes");
    expect(container.textContent).toContain("AUTH_001");
    expect(container.textContent).toContain("401");
    expect(container.textContent).toContain("Invalid credentials");
    expect(container.textContent).toContain("API_001");
    expect(container.textContent).toContain("429");
  });
});
