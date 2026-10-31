import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqCorrelateViewer } from "@/components/req-correlate-viewer";

describe("ReqCorrelateViewer", () => {
  it("renders", () => {
    const { container } = render(
      <ReqCorrelateViewer correlationId="req-001" totalMs={35} success={true}
        hops={[
          { service: "gateway", method: "GET", path: "/api/users", status: 200, durationMs: 5 },
          { service: "user-svc", method: "GET", path: "/users", status: 200, durationMs: 20 },
          { service: "db", method: "SELECT", path: "users", status: 200, durationMs: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Request Trace");
    expect(container.textContent).toContain("35ms");
    expect(container.textContent).toContain("3 hops");
    expect(container.textContent).toContain("req-001");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("user-svc");
    expect(container.textContent).toContain("db");
  });
});
