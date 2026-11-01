import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CliReferenceCard } from "@/components/cli-reference-card";

describe("CliReferenceCard", () => {
  it("renders commands", () => {
    const onCopy = vi.fn();
    const { container, getAllByText } = render(
      <CliReferenceCard title="Quick Commands" onCopy={onCopy} commands={[
        { command: "openskill deploy myapp --env=production", copyable: "openskill deploy myapp --env=production" },
        { command: "openskill logs myapp --tail=100", copyable: "openskill logs myapp --tail=100" },
      ]} />
    );
    expect(container.textContent).toContain("Quick Commands");
    expect(container.textContent).toContain("openskill deploy");
    expect(container.textContent).toContain("openskill logs");
    fireEvent.click(getAllByText("📋")[0]);
    expect(onCopy).toHaveBeenCalled();
  });
});
