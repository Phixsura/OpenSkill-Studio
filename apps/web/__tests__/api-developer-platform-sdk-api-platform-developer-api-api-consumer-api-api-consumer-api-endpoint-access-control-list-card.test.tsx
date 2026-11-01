import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-access-control-list-card";

describe("EndpointAccessControlListCard", () => {
  it("shows rules", () => {
    const rules = [{ id: "r1", path: "/api/admin", consumerId: "c1", action: "deny", reason: "restricted" }];
    const { container } = render(<Card rules={rules} defaultPolicy="allow" appName="App" />);
    expect(container.textContent).toContain("Access Control");
    expect(container.textContent).toContain("/api/admin");
    expect(container.textContent).toContain("deny");
    expect(container.textContent).toContain("Default: allow");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} defaultPolicy="deny" appName="App" />);
    expect(container.textContent).toContain("No ACL rules");
  });
});
