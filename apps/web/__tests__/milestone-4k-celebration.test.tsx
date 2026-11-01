import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone4kCelebration } from "@/components/milestone-4k-celebration";

describe("Milestone4kCelebration", () => {
  const stats = { commits: 1513, lines: 134000, files: 4000,
    backend_services: 890, frontend_components: 790, test_files: 1850 };
  it("renders the celebration", () => {
    const { container } = render(
      <Milestone4kCelebration stats={stats} achievement="🎉 FOUR THOUSAND!" version="9.0.0" />
    );
    expect(container.textContent).toContain("4,000 FILES!");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("1,513");
    expect(container.textContent).toContain("134,000");
    expect(container.textContent).toContain("4,000");
    expect(container.textContent).toContain("v9.0.0");
  });
});
