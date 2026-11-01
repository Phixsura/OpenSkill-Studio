import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFinetunePanel } from "@/components/fleet-finetune-panel";
describe("FleetFinetunePanel", () => { it("renders", () => {
    const { container } = render(<FleetFinetunePanel total={10} running={2} completed={7} failed={1} epochs={70} />);
    expect(container.textContent).toContain("Fine-tuning");
}); });
