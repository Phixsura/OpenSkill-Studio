import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandTotalPanel } from "@/components/grand-total-panel";
describe("GrandTotalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GrandTotalPanel commits={3276} lines={276650} files={9886}
        services={1638} components={1638} tests={3276}
        modules={10} securityFixes={3} status="FULLY OPERATIONAL" />
    );
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("3,276");
    expect(container.textContent).toContain("277K");
    expect(container.textContent).toContain("9,886");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("3 fixes");
  });
});
