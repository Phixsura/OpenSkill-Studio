import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV25_15k } from "@/components/platform-v25-15k";
describe("PlatformV25_15k", () => { it("renders", () => {
    const { container } = render(<PlatformV25_15k />);
    expect(container.textContent).toContain("v25");
    expect(container.textContent).toContain("15,000");
}); });
