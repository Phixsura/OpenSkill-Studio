import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqLoggerPanel } from "@/components/req-logger-panel";
describe("ReqLoggerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqLoggerPanel total={100} byStatus={{ "2xx": 90, "4xx": 8, "5xx": 2 }}
        logs={[
          { method: "GET", path: "/api/users", status: 200, durationMs: 15 },
          { method: "POST", path: "/api/orders", status: 500, durationMs: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Request Log");
    expect(container.textContent).toContain("100 total");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
