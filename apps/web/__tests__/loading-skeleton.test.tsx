import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadingSkeleton } from "@/components/loading-skeleton";

describe("LoadingSkeleton", () => {
  it("renders card skeletons", () => {
    const { container } = render(<LoadingSkeleton layout="card" count={3} />);
    expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });
  it("renders list skeletons", () => {
    const { container } = render(<LoadingSkeleton layout="list" count={2} />);
    expect(container.querySelectorAll(".rounded-full").length).toBeGreaterThan(0);
  });
});
