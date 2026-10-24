import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwLogAnalyzePanel } from "@/components/gw-log-analyze-panel";
describe("GwLogAnalyzePanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwLogAnalyzePanel total={10000} avgMs={45} slowRequests={50}
        byStatus={{ "2xx": 9500, "4xx": 400, "5xx": 100 }}
        topPaths={[{ path: "/api/users", count: 5000 }]} />
    );
    expect(container.textContent).toContain("Gateway Log Analysis");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("45ms avg");
    expect(container.textContent).toContain("50 slow");
    expect(container.textContent).toContain("5xx: 100");
    expect(container.textContent).toContain("/api/users");
  });
});
