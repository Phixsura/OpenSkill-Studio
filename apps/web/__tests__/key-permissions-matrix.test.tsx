import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KeyPermissionsMatrix } from "@/components/key-permissions-matrix";

describe("KeyPermissionsMatrix", () => {
  it("renders matrix", () => {
    const { container } = render(
      <KeyPermissionsMatrix keyName="Production" keyScopes={["read:apps"]}
        endpoints={[
          { endpoint: "GET /api/v1/apps", scopes: ["read:apps"] },
          { endpoint: "POST /api/v1/apps", scopes: ["write:apps"] },
        ]} />
    );
    expect(container.textContent).toContain("Key Permissions");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("GET /api/v1/apps");
    expect(container.textContent).toContain("read:apps");
  });
});
