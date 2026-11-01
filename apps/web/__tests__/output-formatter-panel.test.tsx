import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OutputFormatterPanel } from "@/components/output-formatter-panel";

const mockData = [
  { name: "Alice", age: 30, city: "NYC" },
  { name: "Bob", age: 25, city: "SF" },
];

describe("OutputFormatterPanel", () => {
  it("renders format options", () => {
    const { container } = render(
      <OutputFormatterPanel data={mockData} formattedOutput="" />
    );
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("CSV");
    expect(container.textContent).toContain("Markdown");
    expect(container.textContent).toContain("HTML Table");
  });

  it("shows field selectors", () => {
    const { container } = render(
      <OutputFormatterPanel data={mockData} formattedOutput="" />
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("age");
    expect(container.textContent).toContain("city");
  });

  it("calls onFormat", () => {
    const onFormat = vi.fn();
    const { getByText } = render(
      <OutputFormatterPanel data={mockData} formattedOutput="" onFormat={onFormat} />
    );
    fireEvent.click(getByText("Format as JSON"));
    expect(onFormat).toHaveBeenCalled();
  });

  it("shows formatted output", () => {
    const { container } = render(
      <OutputFormatterPanel data={mockData} formattedOutput='[{"name":"Alice"}]' />
    );
    expect(container.textContent).toContain('{"name":"Alice"}');
  });

  it("calls onCopy", () => {
    const onCopy = vi.fn();
    const { getByText } = render(
      <OutputFormatterPanel data={mockData} formattedOutput="output" onCopy={onCopy} />
    );
    fireEvent.click(getByText("Copy"));
    expect(onCopy).toHaveBeenCalled();
  });
});
