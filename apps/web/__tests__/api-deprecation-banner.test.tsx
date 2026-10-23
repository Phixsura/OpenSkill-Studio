import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDeprecationBanner } from "@/components/api-deprecation-banner";

describe("ApiDeprecationBanner", () => {
  it("shows deprecation", () => {
    const { container } = render(
      <ApiDeprecationBanner path="/api/v1/users" method="GET" sunsetDate="2027-01-01" replacement="/api/v2/users" />
    );
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("/api/v2/users");
  });
  it("no replacement", () => {
    const { container } = render(
      <ApiDeprecationBanner path="/old" method="POST" sunsetDate="2027-06-01" />
    );
    expect(container.textContent).not.toContain("instead");
  });
});
