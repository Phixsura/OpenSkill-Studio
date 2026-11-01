import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UpdateAppDialog } from "@/components/update-app-dialog";

describe("UpdateAppDialog", () => {
  it("shows version change", () => {
    const { container } = render(
      <UpdateAppDialog appName="App" currentVersion="1.0" targetVersion="2.0" breakingChanges={[]} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("1.0 → 2.0");
  });
  it("shows breaking changes", () => {
    const { container } = render(
      <UpdateAppDialog appName="App" currentVersion="1.0" targetVersion="2.0" breakingChanges={["Removed endpoint X"]} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("Removed endpoint X");
    expect(container.textContent).toContain("Update Anyway");
  });
  it("safe update shows Update button", () => {
    const { container } = render(
      <UpdateAppDialog appName="App" currentVersion="1.0" targetVersion="1.1" breakingChanges={[]} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Update");
    expect(btn).toBeTruthy();
  });
});
