import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataPipelineCard from "../src/components/data-pipeline-card";

const stages = [
  {
    stage_id: "extract",
    name: "Extract Data",
    stage_type: "extract",
    status: "completed" as const,
    duration_ms: 1500,
    input_count: 0,
    output_count: 100,
    error: null,
  },
  {
    stage_id: "transform",
    name: "Transform",
    stage_type: "transform",
    status: "running" as const,
    duration_ms: null,
    input_count: 100,
    output_count: 0,
    error: null,
  },
  {
    stage_id: "load",
    name: "Load to DB",
    stage_type: "load",
    status: "pending" as const,
    duration_ms: null,
    input_count: 0,
    output_count: 0,
    error: null,
  },
];

const failedStages = [
  {
    stage_id: "extract",
    name: "Extract",
    stage_type: "extract",
    status: "failed" as const,
    duration_ms: 500,
    input_count: 0,
    output_count: 0,
    error: "connection lost",
  },
  {
    stage_id: "transform",
    name: "Transform",
    stage_type: "transform",
    status: "skipped" as const,
    duration_ms: null,
    input_count: 0,
    output_count: 0,
    error: null,
  },
];

describe("DataPipelineCard", () => {
  it("renders pipeline name and app name", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL Job"
        stages={stages}
        status="running"
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("ETL Job");
    expect(container.textContent).toContain("My App");
  });

  it("shows stage progress", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL"
        stages={stages}
        status="running"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("1/3 stages");
  });

  it("renders stage names", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL"
        stages={stages}
        status="running"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Extract Data");
    expect(container.textContent).toContain("Transform");
    expect(container.textContent).toContain("Load to DB");
  });

  it("shows duration for completed stages", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL"
        stages={stages}
        status="running"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("1.5s");
  });

  it("shows output count", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL"
        stages={stages}
        status="running"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("100 out");
  });

  it("shows error message for failed stage", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="p1"
        pipelineName="ETL"
        stages={failedStages}
        status="failed"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("connection lost");
  });

  it("shows pipeline id", () => {
    const { container } = render(
      <DataPipelineCard
        pipelineId="pipeline-42"
        pipelineName="ETL"
        stages={stages}
        status="running"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("pipeline-42");
  });
});
