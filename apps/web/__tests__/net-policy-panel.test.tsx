import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetPolicyPanel } from "@/components/net-policy-panel";

describe("NetPolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <NetPolicyPanel allowCount={2} denyCount={1}
        policies={[
          { name: "web-to-api", source: "web", destination: "api", port: 8080, action: "allow" },
          { name: "api-to-db", source: "api", destination: "db", port: 5432, action: "allow" },
          { name: "block-ext", source: "external", destination: "db", port: 5432, action: "deny" },
        ]} />
    );
    expect(container.textContent).toContain("Network Policies");
    expect(container.textContent).toContain("2 allow");
    expect(container.textContent).toContain("1 deny");
    expect(container.textContent).toContain("web → api:8080");
    expect(container.textContent).toContain("allow");
    expect(container.textContent).toContain("deny");
  });
});
