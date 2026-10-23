import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NpsSurveyWidget } from "@/components/nps-survey-widget";

describe("NpsSurveyWidget", () => {
  it("renders", () => {
    const { container } = render(<NpsSurveyWidget appName="MyApp" onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("recommend MyApp");
    expect(container.querySelectorAll("button").length).toBe(11); // 0-10
  });
  it("select and submit", () => {
    const fn = vi.fn();
    const { container } = render(<NpsSurveyWidget appName="App" onSubmit={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[9]); // score 9
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Submit")!);
    expect(fn).toHaveBeenCalledWith(9, "");
  });
});
