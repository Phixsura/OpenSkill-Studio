import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThrottleStatusTable } from "@/components/throttle-status-table";

describe("ThrottleStatusTable", () => {
  it("renders table", () => {
    const { container } = render(
      <ThrottleStatusTable entries={[
        { path: "/api/users", served: 5000, throttled: 120, currentRpm: 55, limit: 60 },
        { path: "/api/data", served: 3000, throttled: 0, currentRpm: 10, limit: 100 },
      ]} />
    );
    expect(container.textContent).toContain("Throttle Status");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5000");
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("/api/data");
  });
});
