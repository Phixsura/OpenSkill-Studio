import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RuntimeConfigEditor } from "@/components/runtime-config-editor";

describe("RuntimeConfigEditor", () => {
  const entries = [
    { key: "port", value: 3000, type: "integer", hasDefault: true },
    { key: "debug", value: false, type: "boolean", hasDefault: true },
  ];
  it("renders config entries", () => {
    const { container } = render(
      <RuntimeConfigEditor entries={entries} errors={[]} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("integer");
    expect(container.textContent).toContain("3000");
    expect(container.textContent).toContain("Save Config");
  });
  it("shows errors", () => {
    const { container } = render(
      <RuntimeConfigEditor entries={entries} errors={[{ key: "port", error: "Must be > 0" }]} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("Must be > 0");
  });
});
