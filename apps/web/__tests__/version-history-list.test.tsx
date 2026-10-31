import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionHistoryList } from "@/components/version-history-list";

describe("VersionHistoryList", () => {
  it("renders versions", () => {
    const onRollback = vi.fn();
    const { container, getByText } = render(
      <VersionHistoryList appId="app1" onRollback={onRollback} versions={[
        { version: "2.0.0", changelog: "Major update", latest: true, sizeKb: 500 },
        { version: "1.1.0", changelog: "Bug fixes", latest: false, sizeKb: 450 },
      ]} />
    );
    expect(container.textContent).toContain("Version History");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Latest");
    expect(container.textContent).toContain("Major update");
    fireEvent.click(getByText("Rollback"));
    expect(onRollback).toHaveBeenCalledWith("1.1.0");
  });
});
