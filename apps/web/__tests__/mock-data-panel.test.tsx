import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MockDataPanel } from "@/components/mock-data-panel";
describe("MockDataPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MockDataPanel dataType="users" count={100} fields={["id", "name", "email"]} sampleId="usr_abc123" />
    );
    expect(container.textContent).toContain("Mock Data: users");
    expect(container.textContent).toContain("100 records");
    expect(container.textContent).toContain("3 fields");
    expect(container.textContent).toContain("id, name, email");
    expect(container.textContent).toContain("usr_abc123");
  });
});
