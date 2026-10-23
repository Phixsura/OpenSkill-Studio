import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationStatusPanel } from "@/components/migration-status-panel";

describe("MigrationStatusPanel", () => {
  it("renders and applies", () => {
    const onApply = vi.fn();
    const { container, getByText } = render(
      <MigrationStatusPanel currentVersion="001" total={2} applied={1} pending={1}
        pendingList={[{ version: "002", description: "Add email" }]} onApply={onApply} />
    );
    expect(container.textContent).toContain("Database Migrations");
    expect(container.textContent).toContain("v001");
    expect(container.textContent).toContain("Add email");
    fireEvent.click(getByText("Apply"));
    expect(onApply).toHaveBeenCalledWith("002");
  });
});
