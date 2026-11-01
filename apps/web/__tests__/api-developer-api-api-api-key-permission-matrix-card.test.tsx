import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiApiKeyPermissionMatrixCard from "../src/components/api-developer-api-api-api-key-permission-matrix-card";

const perms = [{
  key_id: "sk-prod-1", allowed_count: 3, denied_count: 1,
  endpoints: [{ endpoint: "/api/users", methods: ["GET", "POST"] }],
}];

describe("APIDeveloperAPIApiApiKeyPermissionMatrixCard", () => {
  it("shows permissions", () => {
    const { container } = render(<APIDeveloperAPIApiApiKeyPermissionMatrixCard permissions={perms} appName="App" />);
    expect(container.textContent).toContain("Key Permissions");
    expect(container.textContent).toContain("sk-prod-1");
    expect(container.textContent).toContain("3 allowed");
    expect(container.textContent).toContain("/api/users [GET,POST]");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiApiKeyPermissionMatrixCard permissions={[]} appName="App" />);
    expect(container.textContent).toContain("No key permissions");
  });
});
