import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPendulum } from "@/components/platform-pendulum";
describe("PlatformPendulum", () => { it("renders", () => {
    const { container } = render(<PlatformPendulum />);
    expect(container.textContent).toContain("PENDULUM");
    expect(container.textContent).toContain("Perpetual");
}); });
