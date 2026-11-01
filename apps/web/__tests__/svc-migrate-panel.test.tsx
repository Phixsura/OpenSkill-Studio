import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcMigratePanel } from "@/components/svc-migrate-panel";
describe("SvcMigratePanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcMigratePanel completed={1} inProgress={1}
        migrations={[
          { service: "api", from: "heroku", to: "k8s", status: "completed", progressPct: 100 },
          { service: "worker", from: "ec2", to: "k8s", status: "in_progress", progressPct: 50 },
        ]} />
    );
    expect(container.textContent).toContain("Service Migrations");
    expect(container.textContent).toContain("1 done");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("api: heroku → k8s");
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("50%");
  });
});
