import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecutionResultCard } from "@/components/execution-result-card";

describe("ExecutionResultCard", () => {
  it("shows success", () => {
    const { container } = render(<ExecutionResultCard success={true} durationMs={150} memoryMb={64} logCount={3} />);
    expect(container.textContent).toContain("Success");
    expect(container.textContent).toContain("150ms");
  });

  it("shows failure with error", () => {
    const { container } = render(<ExecutionResultCard success={false} durationMs={5000} memoryMb={128} logCount={10} error="TimeoutError" />);
    expect(container.textContent).toContain("Failed");
    expect(container.textContent).toContain("TimeoutError");
  });

  it("shows output", () => {
    const { container } = render(<ExecutionResultCard success={true} durationMs={100} memoryMb={32} logCount={0} output={{ result: "ok" }} />);
    expect(container.textContent).toContain("result");
  });

  it("shows metrics", () => {
    const { container } = render(<ExecutionResultCard success={true} durationMs={200} memoryMb={96.5} logCount={5} />);
    expect(container.textContent).toContain("96.5MB");
    expect(container.textContent).toContain("5 logs");
  });
});
