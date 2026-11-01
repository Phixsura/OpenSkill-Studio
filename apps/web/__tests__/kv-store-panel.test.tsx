import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KVStorePanel } from "@/components/kv-store-panel";

const mockEntries = [
  { key: "user:1", value: '{"name":"alice"}', sizeBytes: 16, hasTtl: false },
  { key: "session:abc", value: "active", sizeBytes: 6, hasTtl: true },
  { key: "counter", value: "42", sizeBytes: 2, hasTtl: false },
];

describe("KVStorePanel", () => {
  it("renders entries with keys", () => {
    const { container } = render(<KVStorePanel entries={mockEntries} totalCount={3} />);
    expect(container.textContent).toContain("user:1");
    expect(container.textContent).toContain("counter");
    expect(container.textContent).toContain("3 keys");
  });

  it("shows TTL indicator", () => {
    const { container } = render(<KVStorePanel entries={mockEntries} totalCount={3} />);
    expect(container.textContent).toContain("⏳");
  });

  it("calls onDelete", () => {
    const onDelete = vi.fn();
    const { container } = render(<KVStorePanel entries={mockEntries} totalCount={3} onDelete={onDelete} />);
    const deleteBtn = container.querySelectorAll("button");
    const del = Array.from(deleteBtn).find(b => b.textContent === "✕");
    if (del) fireEvent.click(del);
    expect(onDelete).toHaveBeenCalled();
  });

  it("opens set form", () => {
    const { getByText, getByPlaceholderText } = render(
      <KVStorePanel entries={[]} totalCount={0} />
    );
    fireEvent.click(getByText("+ Set"));
    expect(getByPlaceholderText("Key")).toBeDefined();
  });
});
