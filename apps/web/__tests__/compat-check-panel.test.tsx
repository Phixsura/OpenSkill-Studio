import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatCheckPanel } from "@/components/compat-check-panel";
describe("CompatCheckPanel", () => {
  it("renders breaking", () => {
    const { container } = render(
      <CompatCheckPanel compatible={false} fromVersion="1.0" toVersion="2.0" warnings={1}
        breaking={[
          { type: "field_removed", field: "age" },
          { type: "type_changed", field: "name" },
        ]} />
    );
    expect(container.textContent).toContain("API Compatibility");
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("2 breaking");
    expect(container.textContent).toContain("age");
    expect(container.textContent).toContain("field removed");
    expect(container.textContent).toContain("1 warning");
  });
});
