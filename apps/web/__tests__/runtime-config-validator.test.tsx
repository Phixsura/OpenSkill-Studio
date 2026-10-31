import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RuntimeConfigValidator } from "@/components/runtime-config-validator";

describe("RuntimeConfigValidator", () => {
  it("renders validation", () => {
    const { container } = render(
      <RuntimeConfigValidator valid={false} checked={3}
        errors={[{ key: "port", error: "expected_int" }, { key: "host", error: "missing_required" }]}
        warnings={[{ key: "old_flag", warning: "deprecated_config" }]} />
    );
    expect(container.textContent).toContain("Runtime Config");
    expect(container.textContent).toContain("3 keys checked");
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("expected int");
    expect(container.textContent).toContain("host");
    expect(container.textContent).toContain("deprecated config");
  });
});
