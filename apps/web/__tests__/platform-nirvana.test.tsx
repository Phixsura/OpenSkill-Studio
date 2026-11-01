import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformNirvana } from "@/components/platform-nirvana";
describe("PlatformNirvana", () => { it("renders", () => {
    const { container } = render(<PlatformNirvana />);
    expect(container.textContent).toContain("NIRVANA");
    expect(container.textContent).toContain("Commit");
}); });
