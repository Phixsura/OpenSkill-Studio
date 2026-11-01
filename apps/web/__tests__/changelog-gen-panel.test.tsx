import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogGenPanel } from "@/components/changelog-gen-panel";

const mockStats = { total: 10, conventional: 8, breaking: 1, byType: { feat: 4, fix: 3, docs: 1 } };

describe("ChangelogGenPanel", () => {
  it("calls onGenerate", () => {
    const onGen = vi.fn();
    const { getByText } = render(<ChangelogGenPanel generatedMarkdown="" stats={null} onGenerate={onGen} />);
    fireEvent.click(getByText("Generate"));
    expect(onGen).toHaveBeenCalledWith("1.0.0");
  });

  it("shows generated markdown", () => {
    const { container } = render(<ChangelogGenPanel generatedMarkdown="## 1.0.0\n- feat: new feature" stats={mockStats} />);
    expect(container.textContent).toContain("1.0.0");
    expect(container.textContent).toContain("8/10 conventional");
  });
});
