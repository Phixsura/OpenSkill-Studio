import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClientErrPanel } from "@/components/client-err-panel";
describe("ClientErrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ClientErrPanel total={200} ratePct={2} healthy={true}
        byStatus={{ "400": 100, "404": 80, "422": 20 }}
        topEndpoints={[
          { endpoint: "/api/users", count: 100 },
          { endpoint: "/api/orders", count: 50 },
        ]} />
    );
    expect(container.textContent).toContain("Client Errors (4xx)");
    expect(container.textContent).toContain("2% rate");
    expect(container.textContent).toContain("200 errors");
    expect(container.textContent).toContain("400: 100");
    expect(container.textContent).toContain("/api/users");
  });
});
