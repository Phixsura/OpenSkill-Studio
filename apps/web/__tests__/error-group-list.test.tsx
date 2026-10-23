import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorGroupList } from "@/components/error-group-list";

describe("ErrorGroupList", () => {
  it("renders groups", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <ErrorGroupList totalErrors={50} uniqueGroups={3} onSelect={onSelect}
        groups={[
          { fingerprint: "abc123", message: "TypeError: null", count: 30, affectedUsers: 10, lastSeen: "5m ago" },
          { fingerprint: "def456", message: "RangeError", count: 15, affectedUsers: 5, lastSeen: "1h ago" },
        ]} />
    );
    expect(container.textContent).toContain("Error Groups");
    expect(container.textContent).toContain("50 errors");
    expect(container.textContent).toContain("3 groups");
    expect(container.textContent).toContain("TypeError: null");
    expect(container.textContent).toContain("30×");
    expect(container.textContent).toContain("10 users");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onSelect).toHaveBeenCalledWith("abc123");
  });
});
