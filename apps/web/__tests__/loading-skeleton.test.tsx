import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadingSkeleton } from "@/components/loading-skeleton";

describe("LoadingSkeleton", () => {
  const rows = [
    { type: "circle", size: 48 },
    { type: "line", width: "60%", height: 16 },
    { type: "rect", width: "100%", height: 80 },
  ];
  it("renders skeleton elements", () => {
    const { container } = render(<LoadingSkeleton rows={rows} count={1} />);
    expect(container.querySelector(".animate-pulse")).toBeTruthy();
    expect(container.querySelector(".rounded-full")).toBeTruthy(); // circle
    expect(container.querySelector(".rounded-lg")).toBeTruthy(); // rect
  });
  it("renders multiple", () => {
    const { container } = render(<LoadingSkeleton rows={[{ type: "line" }]} count={3} />);
    const groups = container.querySelectorAll(".space-y-3");
    expect(groups.length).toBe(3);
  });
});
