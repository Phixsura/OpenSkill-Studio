import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionedConfigPanel } from "@/components/versioned-config-panel";

const mockVersions = [
  { version: 1, author: "admin", message: "Initial", createdAt: "2024-01-01", keyCount: 3 },
  { version: 2, author: "dev", message: "Updated theme", createdAt: "2024-01-15", keyCount: 4 },
];
const mockData = { theme: "dark", lang: "en", debug: false };
const mockDiff = {
  added: { debug: false }, removed: { old_key: "val" },
  changed: { theme: { from: "light", to: "dark" } }, hasChanges: true,
};

describe("VersionedConfigPanel", () => {
  it("renders current config as JSON", () => {
    const { container } = render(
      <VersionedConfigPanel versions={mockVersions} currentData={mockData} diff={null} />
    );
    expect(container.textContent).toContain('"theme"');
    expect(container.textContent).toContain('"dark"');
  });

  it("shows version history", () => {
    const { getByText, container } = render(
      <VersionedConfigPanel versions={mockVersions} currentData={mockData} diff={null} />
    );
    fireEvent.click(getByText("History (2)"));
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("Initial");
    expect(container.textContent).toContain("3 keys");
  });

  it("shows diff view", () => {
    const { getByText, container } = render(
      <VersionedConfigPanel versions={mockVersions} currentData={mockData} diff={mockDiff} />
    );
    fireEvent.click(getByText("Diff"));
    expect(container.textContent).toContain("+ debug");
    expect(container.textContent).toContain("- old_key");
    expect(container.textContent).toContain("~ theme");
  });

  it("calls onRollback", () => {
    const onRollback = vi.fn();
    const { getByText, getAllByText } = render(
      <VersionedConfigPanel versions={mockVersions} currentData={mockData} diff={null} onRollback={onRollback} />
    );
    fireEvent.click(getByText("History (2)"));
    fireEvent.click(getAllByText("Rollback")[0]);
    expect(onRollback).toHaveBeenCalledWith(1);
  });
});
