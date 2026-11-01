import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureBoard } from "@/components/feature-board";

describe("FeatureBoard", () => {
  const requests = [
    { title: "Dark mode", status: "open", votes: 25, author: "Alice", category: "ui" },
    { title: "Export CSV", status: "planned", votes: 10, author: "Bob", category: "data" },
  ];
  it("renders requests", () => {
    const { container } = render(<FeatureBoard requests={requests} totalVotes={35} onVote={vi.fn()} />);
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("planned");
    expect(container.textContent).toContain("35 votes");
  });
  it("vote click", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureBoard requests={requests} totalVotes={35} onVote={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("Dark mode");
  });
});
