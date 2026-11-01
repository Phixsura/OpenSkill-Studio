import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestLogViewer } from "@/components/request-log-viewer";

describe("RequestLogViewer", () => {
  it("renders log", () => {
    const { container } = render(
      <RequestLogViewer total={100} errorRate={5.0} avgDurationMs={65}
        entries={[
          { id: "r1", method: "GET", path: "/api/users", status: 200, durationMs: 50, userId: "", error: false },
          { id: "r2", method: "POST", path: "/api/apps", status: 500, durationMs: 200, userId: "", error: true },
        ]} />
    );
    expect(container.textContent).toContain("Request Log");
    expect(container.textContent).toContain("100 requests");
    expect(container.textContent).toContain("5% errors");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
