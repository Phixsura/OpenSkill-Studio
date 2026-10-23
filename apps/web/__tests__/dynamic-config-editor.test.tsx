import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DynamicConfigEditor } from "@/components/dynamic-config-editor";

describe("DynamicConfigEditor", () => {
  const configs = [
    { key: "MAX_RETRIES", value: 3, value_type: "number", description: "Max retries",
      environment: "production", updated_at: "2026-10-23" },
    { key: "DEBUG", value: false, value_type: "boolean", description: "",
      environment: "all", updated_at: "2026-10-22" },
  ];
  it("renders", () => {
    const { container } = render(
      <DynamicConfigEditor configs={configs} environment="production"
        onUpdate={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("Dynamic Config");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("MAX_RETRIES");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("🔢");
    expect(container.textContent).toContain("DEBUG");
  });
});
