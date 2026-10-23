import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PayloadInspector } from "@/components/payload-inspector";

describe("PayloadInspector", () => {
  it("renders inspector", () => {
    const { container } = render(
      <PayloadInspector formatted='{"event": "test"}' sizeDisplay="18 B"
        depth={1} fieldCount={1} fields={["event"]} warnings={[]} />
    );
    expect(container.textContent).toContain("Payload Inspector");
    expect(container.textContent).toContain("18 B");
    expect(container.textContent).toContain("1 fields");
    expect(container.textContent).toContain("event");
    expect(container.textContent).toContain('"event": "test"');
  });
});
