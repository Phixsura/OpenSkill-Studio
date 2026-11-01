import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformGwStatus } from "@/components/platform-gw-status";

describe("PlatformGwStatus", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformGwStatus status="healthy" totalRequests={50000}
        middleware={["auth", "rate_limit", "logging"]}
        routes={[
          { path: "/api/users", service: "user-svc", methods: ["GET", "POST"] },
          { path: "/api/orders", service: "order-svc", methods: ["GET"] },
        ]} />
    );
    expect(container.textContent).toContain("Platform Gateway");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("auth → rate_limit → logging");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("user-svc");
  });
});
