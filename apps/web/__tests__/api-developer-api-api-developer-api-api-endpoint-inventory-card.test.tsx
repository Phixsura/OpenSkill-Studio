import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiEndpointInventoryCard from "../src/components/api-developer-api-api-developer-api-api-endpoint-inventory-card";

const endpoints = [
  { endpoint_id: "e1", method: "GET", path: "/api/v1/users", version: "v1", status: "active", documented: true, tags: ["users"] },
  { endpoint_id: "e2", method: "POST", path: "/api/v1/orders", version: "v1", status: "deprecated", documented: false, tags: [] },
];
const stats = { total: 2, active: 1, deprecated: 1, documented: 1, undocumented: 1 };

describe("APIDeveloperAPIApiDeveloperApiApiEndpointInventoryCard", () => {
  it("shows inventory", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiEndpointInventoryCard endpoints={endpoints} stats={stats} appName="App" />);
    expect(container.textContent).toContain("Endpoint Inventory");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("1 documented");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("deprecated");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiEndpointInventoryCard endpoints={[]} stats={{ total: 0, active: 0, deprecated: 0, documented: 0, undocumented: 0 }} appName="App" />);
    expect(container.textContent).toContain("No endpoints");
  });
});
