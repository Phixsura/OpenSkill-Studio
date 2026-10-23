import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogSearchPanel } from "@/components/log-search-panel";

describe("LogSearchPanel", () => {
  it("renders and searches", () => {
    const onSearch = vi.fn();
    const { container, getByText } = render(
      <LogSearchPanel total={2} onSearch={onSearch} logs={[
        { level: "error", service: "api", message: "Connection timeout" },
        { level: "info", service: "worker", message: "Job completed" },
      ]} />
    );
    expect(container.textContent).toContain("Log Search");
    expect(container.textContent).toContain("2 results");
    expect(container.textContent).toContain("Connection timeout");
    fireEvent.click(getByText("Search"));
    expect(onSearch).toHaveBeenCalled();
  });
});
