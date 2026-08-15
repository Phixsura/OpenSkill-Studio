import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(() => Promise.resolve({ download_url: "https://s3/test.png" })),
  ApiError: class extends Error {},
}));

import { VersionCompare } from "@/components/version-compare";

const ITEMS = [
  { id: "i1", file_name: "v1.png", mime_type: "image/png", version: 1, note: null },
  { id: "i2", file_name: "v2.png", mime_type: "image/png", version: 2, note: "fixed color" },
  { id: "i3", file_name: "v3.png", mime_type: "image/png", version: 3, note: null },
];

describe("VersionCompare", () => {
  it("renders nothing with fewer than two versions", () => {
    const { container } = render(
      <VersionCompare items={[ITEMS[0]!]} downloadPath={(id) => `/files/${id}`} />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("shows compare toggle with version count", () => {
    render(<VersionCompare items={ITEMS} downloadPath={(id) => `/files/${id}`} />);
    expect(screen.getByText(/Compare versions \(3\)/)).toBeDefined();
  });

  it("opens side-by-side with latest vs previous by default", () => {
    render(<VersionCompare items={ITEMS} downloadPath={(id) => `/files/${id}`} />);
    fireEvent.click(screen.getByText(/Compare versions/));
    // Latest badge present
    expect(screen.getByText(/v3 · latest/)).toBeDefined();
    // Previous version selected on the left
    expect(screen.getByText("v2")).toBeDefined();
    // Note shown for the version that has one
    expect(screen.getByText(/fixed color/)).toBeDefined();
  });

  it("toggle hides comparison", () => {
    render(<VersionCompare items={ITEMS} downloadPath={(id) => `/files/${id}`} />);
    fireEvent.click(screen.getByText(/Compare versions/));
    fireEvent.click(screen.getByText("Hide comparison"));
    expect(screen.queryByText(/v3 · latest/)).toBeNull();
  });
});
