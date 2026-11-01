import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SdkGenPanel } from "@/components/sdk-gen-panel";
describe("SdkGenPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SdkGenPanel sdkName="openskill-sdk" version="1.0.0" totalMethods={3} coveragePct={100}
        methods={[
          { name: "api_v1_users", httpMethod: "GET", path: "/api/v1/users" },
          { name: "api_v1_orders", httpMethod: "POST", path: "/api/v1/orders" },
        ]} />
    );
    expect(container.textContent).toContain("SDK: openskill-sdk v1.0.0");
    expect(container.textContent).toContain("3 methods");
    expect(container.textContent).toContain("100% coverage");
    expect(container.textContent).toContain("api_v1_users()");
    expect(container.textContent).toContain("GET");
  });
});
