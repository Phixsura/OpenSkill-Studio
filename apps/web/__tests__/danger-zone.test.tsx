import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DangerZone } from "@/components/danger-zone";

describe("DangerZone", () => {
  it("shows delete", () => {
    const { container } = render(<DangerZone canDelete={true} canArchive={false} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("Delete");
  });
  it("shows archive", () => {
    const { container } = render(<DangerZone canDelete={false} canArchive={true} onArchive={vi.fn()} />);
    expect(container.textContent).toContain("Archive");
  });
  it("null when nothing allowed", () => {
    const { container } = render(<DangerZone canDelete={false} canArchive={false} />);
    expect(container.innerHTML).toBe("");
  });
});
