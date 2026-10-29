import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRequestTransformCard from "../src/components/api-request-transform-card";

const rules = [
  { rule_id: "r1", action: "add_header", key: "X-Tenant", value: "acme" },
  { rule_id: "r2", action: "rewrite_path", key: "/v1/", value: "/v2/" },
];

describe("APIRequestTransformCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIRequestTransformCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Request Transform");
    expect(container.textContent).toContain("2 rules");
  });

  it("shows action labels and keys", () => {
    const { container } = render(<APIRequestTransformCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Add Header");
    expect(container.textContent).toContain("X-Tenant");
    expect(container.textContent).toContain("Rewrite Path");
  });

  it("shows empty state", () => {
    const { container } = render(<APIRequestTransformCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No transform rules");
  });
});
