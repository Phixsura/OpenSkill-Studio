import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-response-header-policy-card";

describe("ResponseHeaderPolicyCard", () => {
  it("shows policies", () => {
    const policies = [{ policy_id: "p1", endpoint: "/api/users", add_count: 3, remove_count: 1 }];
    const { container } = render(<Card policies={policies} appName="App" />);
    expect(container.textContent).toContain("Response Headers");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("+3 −1");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} appName="App" />);
    expect(container.textContent).toContain("No header policies");
  });
});
