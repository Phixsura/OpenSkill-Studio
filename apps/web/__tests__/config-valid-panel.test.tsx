import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigValidPanel } from "@/components/config-valid-panel";

describe("ConfigValidPanel", () => {
  it("renders errors", () => {
    const { container } = render(
      <ConfigValidPanel valid={false} fieldsChecked={3}
        errors={[
          { field: "port", error: "expected int", severity: "error" },
          { field: "host", error: "required", severity: "error" },
        ]} />
    );
    expect(container.textContent).toContain("Config Validator");
    expect(container.textContent).toContain("2 issues");
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("expected int");
    expect(container.textContent).toContain("host");
  });
});
