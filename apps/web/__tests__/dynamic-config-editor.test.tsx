import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DynamicConfigEditor } from "@/components/dynamic-config-editor";

describe("DynamicConfigEditor", () => {
  it("renders flags", () => {
    const { container } = render(
      <DynamicConfigEditor onUpdate={vi.fn()} flags={[
        { key: "max_retries", value: 3, description: "Max retries", type: "int", owner: "platform" },
        { key: "debug_mode", value: false, description: "Debug", type: "bool", owner: "dev" },
      ]} />
    );
    expect(container.textContent).toContain("Dynamic Config");
    expect(container.textContent).toContain("2 flags");
    expect(container.textContent).toContain("max_retries");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("debug_mode");
    expect(container.textContent).toContain("platform");
  });
});
