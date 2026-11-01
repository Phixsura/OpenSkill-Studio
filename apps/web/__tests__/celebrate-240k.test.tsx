import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Celebrate240k } from "@/components/celebrate-240k";

describe("Celebrate240k", () => {
  it("renders", () => {
    const { container } = render(<Celebrate240k />);
    expect(container.textContent).toContain("240,000 LINES");
    expect(container.textContent).toContain("2,786");
    expect(container.textContent).toContain("8,238+");
    expect(container.textContent).toContain("ALL SYSTEMS GREEN");
    expect(container.textContent).toContain("250K");
  });
});
