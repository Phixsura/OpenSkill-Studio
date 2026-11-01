import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformLodestone } from "@/components/platform-lodestone";
describe("PlatformLodestone", () => { it("renders", () => {
    const { container } = render(<PlatformLodestone />);
    expect(container.textContent).toContain("LODESTONE");
    expect(container.textContent).toContain("IMPOSSIBLE");
}); });
