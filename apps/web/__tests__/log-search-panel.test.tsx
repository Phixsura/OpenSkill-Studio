import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogSearchPanel } from "@/components/log-search-panel";

describe("LogSearchPanel", () => {
  it("renders logs", () => {
    const { container } = render(
      <LogSearchPanel matched={2} total={10} services={["api"]} onSearch={vi.fn()}
        levelCounts={{ error: 3, info: 7 }}
        logs={[
          { level: "error", service: "api", message: "Connection timeout" },
          { level: "info", service: "api", message: "OK" },
        ]} />
    );
    expect(container.textContent).toContain("Log Search");
    expect(container.textContent).toContain("2/10");
    expect(container.textContent).toContain("Connection timeout");
    expect(container.textContent).toContain("error");
  });
});
