import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiAccessControlMatrixCard from "../src/components/api-developer-api-api-access-control-matrix-card";

const rules = [
  { endpoint: "/api/admin", method: "GET", allowed_roles: ["admin"], public: false },
  { endpoint: "/api/health", method: "GET", allowed_roles: [], public: true },
];

describe("APIDeveloperAPIApiAccessControlMatrixCard", () => {
  it("shows access rules", () => {
    const { container } = render(<APIDeveloperAPIApiAccessControlMatrixCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Access Control Matrix");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("1 public");
    expect(container.textContent).toContain("/api/admin");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("public");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiAccessControlMatrixCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No access rules");
  });
});
