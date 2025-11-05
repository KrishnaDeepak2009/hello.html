import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


BOX_WIDTH = 2.4
BOX_HEIGHT = 1.2


def add_box(ax, label, xy, color="#f2f2f2", edge="#333333"):
    x, y = xy
    box = FancyBboxPatch(
        (x, y),
        BOX_WIDTH,
        BOX_HEIGHT,
        boxstyle="round,pad=0.3",
        linewidth=1.5,
        facecolor=color,
        edgecolor=edge,
        mutation_aspect=1.0,
    )
    ax.add_patch(box)
    ax.text(
        x + BOX_WIDTH / 2,
        y + BOX_HEIGHT / 2,
        label,
        ha="center",
        va="center",
        fontsize=10,
        wrap=True,
    )


def center(xy):
    x, y = xy
    return (x + BOX_WIDTH / 2, y + BOX_HEIGHT / 2)


def add_arrow(ax, start_xy, end_xy, text=None, text_offset=(0, 0), style="-|>"):
    arrow = FancyArrowPatch(
        posA=center(start_xy),
        posB=center(end_xy),
        arrowstyle=style,
        mutation_scale=15,
        linewidth=1.2,
        color="#4a4a4a",
        connectionstyle="arc3",
    )
    ax.add_patch(arrow)
    if text:
        sx, sy = center(start_xy)
        ex, ey = center(end_xy)
        tx = (sx + ex) / 2 + text_offset[0]
        ty = (sy + ey) / 2 + text_offset[1]
        ax.text(tx, ty, text, fontsize=9, ha="center", va="center")


def main():
    plt.rcParams["pdf.fonttype"] = 42

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")

    boxes = {
        "SFTP Source": (0.5, 6.5),
        "S3 Landing Zone\n(Encrypted Buckets)": (3.5, 6.5),
        "Snowpipe Batch\nOrchestration": (6.5, 6.5),
        "Snowflake Raw\nStaging Tables": (9.5, 6.5),
        "Transform &\nData Quality Tasks": (6.5, 4.0),
        "Snowflake Final\nAnalytics Tables": (9.5, 4.0),
        "Kinesis Stream\n(Real-time JSON)": (0.5, 2.5),
        "AWS Lambda /\nKinesis Data Firehose": (3.5, 2.5),
        "Snowpipe Streaming": (6.5, 2.5),
        "Monitoring &\nAlerting": (3.5, 0.5),
        "Data Catalog &\nGovernance": (6.5, 0.5),
        "Analytics & BI\nConsumers": (9.5, 1.0),
    }

    for label, xy in boxes.items():
        add_box(ax, label, xy)

    add_arrow(ax, boxes["SFTP Source"], boxes["S3 Landing Zone\n(Encrypted Buckets)"], "Twice daily\ncompressed files")
    add_arrow(ax, boxes["S3 Landing Zone\n(Encrypted Buckets)"], boxes["Snowpipe Batch\nOrchestration"], "Event notifications")
    add_arrow(ax, boxes["Snowpipe Batch\nOrchestration"], boxes["Snowflake Raw\nStaging Tables"], "Automatic load")
    add_arrow(ax, boxes["Snowflake Raw\nStaging Tables"], boxes["Transform &\nData Quality Tasks"], "Tasks / Streams")
    add_arrow(ax, boxes["Transform &\nData Quality Tasks"], boxes["Snowflake Final\nAnalytics Tables"], "ELT / dbt")
    add_arrow(ax, boxes["Snowflake Final\nAnalytics Tables"], boxes["Analytics & BI\nConsumers"], "Dashboards, ML")

    add_arrow(ax, boxes["Kinesis Stream\n(Real-time JSON)"], boxes["AWS Lambda /\nKinesis Data Firehose"], "Buffer & enrich")
    add_arrow(ax, boxes["AWS Lambda /\nKinesis Data Firehose"], boxes["Snowpipe Streaming"], "Streaming ingestion")
    add_arrow(ax, boxes["Snowpipe Streaming"], boxes["Snowflake Raw\nStaging Tables"], "Sub-5 min latency", text_offset=(0, -0.4))

    add_arrow(ax, boxes["Monitoring &\nAlerting"], boxes["Snowpipe Batch\nOrchestration"], "Load failures")
    add_arrow(ax, boxes["Monitoring &\nAlerting"], boxes["Snowpipe Streaming"], "Latency alerts")
    add_arrow(ax, boxes["Monitoring &\nAlerting"], boxes["Transform &\nData Quality Tasks"], "DQ scorecards")

    add_arrow(ax, boxes["Data Catalog &\nGovernance"], boxes["Snowflake Raw\nStaging Tables"], "Schema registry", text_offset=(0.0, -0.3))
    add_arrow(ax, boxes["Data Catalog &\nGovernance"], boxes["Snowflake Final\nAnalytics Tables"], "Access policies", text_offset=(0.0, -0.3))

    ax.text(
        0.5,
        8.5,
        "Snowflake Ingestion & Analytics Architecture",
        fontsize=16,
        fontweight="bold",
        ha="left",
    )

    ax.text(
        0.5,
        8.1,
        "Supports batch SFTP loads (<1 GB compressed) and near real-time Kinesis streams; targets <30 min end-to-end latency.",
        fontsize=10,
        ha="left",
    )

    fig.tight_layout()
    fig.savefig("architecture_diagram.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
