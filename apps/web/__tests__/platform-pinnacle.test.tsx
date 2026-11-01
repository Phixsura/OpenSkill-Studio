import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPinnacle } from "@/components/platform-pinnacle";
describe("PlatformPinnacle", () => { it("renders", () => {
    const { container } = render(<PlatformPinnacle />);
    expect(container.textContent).toContain("PINNACLE");
    expect(container.textContent).toContain("0 falls");
}); });
