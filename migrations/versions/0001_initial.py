"""Create the fresh 14-table animation platform database."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channels",
        sa.Column("channel_id", sa.String(36), primary_key=True), sa.Column("name", sa.String(200), nullable=False),
        sa.Column("language", sa.String(32), nullable=False), sa.Column("niche", sa.String(200), nullable=False),
        sa.Column("audience", sa.String(200), nullable=False), sa.Column("dna_json", sa.Text()), sa.Column("voice_profile_json", sa.Text()),
        sa.Column("created_at", sa.String(40), nullable=False), sa.Column("updated_at", sa.String(40), nullable=False),
        sa.Column("visual_style_hash", sa.String(71)), sa.Column("performance_style_hash", sa.String(71)), sa.Column("narration_identity_hash", sa.String(71)),
    )
    op.create_table("projects", sa.Column("project_id", sa.String(36), primary_key=True), sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("created_at", sa.String(40), nullable=False), sa.Column("updated_at", sa.String(40), nullable=False))
    op.create_index("ix_projects_channel_id", "projects", ["channel_id"])
    op.create_table(
        "artifacts", sa.Column("artifact_id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="RESTRICT")),
        sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False), sa.Column("logical_key", sa.String(300), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False), sa.Column("sha256", sa.String(71), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False), sa.Column("approved_at", sa.String(40)),
        sa.Column("parents_json", sa.Text(), nullable=False), sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False), sa.UniqueConstraint("channel_id", "logical_key", "version"),
    )
    op.create_index("ix_artifacts_project_id", "artifacts", ["project_id"])
    op.create_index("ix_artifacts_channel_id", "artifacts", ["channel_id"])
    op.create_index("ix_artifacts_project_kind", "artifacts", ["project_id", "kind"])
    op.create_table("project_stage_heads", sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True), sa.Column("stage_key", sa.String(32), primary_key=True), sa.Column("artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id", ondelete="RESTRICT"), nullable=False), sa.Column("approval_status", sa.String(24), nullable=False), sa.Column("updated_at", sa.String(40), nullable=False))
    op.create_table("authoring_reservations", sa.Column("reservation_id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False), sa.Column("stage_key", sa.String(32), nullable=False), sa.Column("artifact_id", sa.String(36), nullable=False, unique=True), sa.Column("source_hash", sa.String(71), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("created_at", sa.String(40), nullable=False), sa.Column("consumed_at", sa.String(40)))
    op.create_index("uq_authoring_pending_stage", "authoring_reservations", ["project_id", "stage_key"], unique=True, sqlite_where=sa.text("status = 'pending'"))
    op.create_table("assets", sa.Column("asset_id", sa.String(36), primary_key=True), sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False), sa.Column("kind", sa.String(24), nullable=False), sa.Column("semantic_key", sa.String(64), nullable=False), sa.Column("display_name", sa.String(200), nullable=False), sa.Column("created_at", sa.String(40), nullable=False), sa.UniqueConstraint("channel_id", "kind", "semantic_key"), sa.CheckConstraint("kind IN ('character','background','prop')"))
    op.create_table("rigs", sa.Column("rig_id", sa.String(36), primary_key=True), sa.Column("asset_id", sa.String(36), sa.ForeignKey("assets.asset_id", ondelete="RESTRICT"), nullable=False), sa.Column("created_at", sa.String(40), nullable=False))
    op.create_table("rig_versions", sa.Column("rig_version_id", sa.String(36), primary_key=True), sa.Column("rig_id", sa.String(36), sa.ForeignKey("rigs.rig_id", ondelete="RESTRICT"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("manifest_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id"), nullable=False), sa.Column("profile_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id"), nullable=False), sa.Column("spine_json_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id"), nullable=False), sa.Column("atlas_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id"), nullable=False), sa.Column("atlas_png_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id"), nullable=False), sa.Column("approved_at", sa.String(40)), sa.UniqueConstraint("rig_id", "version"))
    op.create_table("asset_versions", sa.Column("asset_version_id", sa.String(36), primary_key=True), sa.Column("asset_id", sa.String(36), sa.ForeignKey("assets.asset_id", ondelete="RESTRICT"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("view", sa.String(32), nullable=False), sa.Column("style_hash", sa.String(71), nullable=False), sa.Column("image_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id")), sa.Column("rig_version_id", sa.String(36), sa.ForeignKey("rig_versions.rig_version_id", ondelete="RESTRICT")), sa.Column("capabilities_json", sa.Text(), nullable=False), sa.Column("source_hashes_json", sa.Text(), nullable=False), sa.Column("approved_at", sa.String(40)), sa.UniqueConstraint("asset_id", "version"))
    op.create_table("project_asset_bindings", sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True), sa.Column("requirement_id", sa.String(128), primary_key=True), sa.Column("asset_version_id", sa.String(36), sa.ForeignKey("asset_versions.asset_version_id", ondelete="RESTRICT"), nullable=False), sa.Column("rig_version_id", sa.String(36), sa.ForeignKey("rig_versions.rig_version_id", ondelete="RESTRICT")), sa.Column("approved_at", sa.String(40)))
    op.create_table("motion_templates", sa.Column("motion_id", sa.String(36), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("action_kind", sa.String(40), nullable=False), sa.Column("template_json", sa.Text(), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.UniqueConstraint("name", "version"))
    op.create_table("operations", sa.Column("operation_id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False), sa.Column("kind", sa.String(40), nullable=False), sa.Column("idempotency_key", sa.String(128)), sa.Column("input_hash", sa.String(71), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("next_reconcile_at", sa.String(40)), sa.Column("lease_owner", sa.String(128)), sa.Column("lease_token", sa.String(128)), sa.Column("lease_expires_at", sa.String(40)), sa.Column("attempt", sa.Integer(), nullable=False), sa.Column("created_at", sa.String(40), nullable=False), sa.Column("updated_at", sa.String(40), nullable=False), sa.Column("error_code", sa.String(64)), sa.Column("error_details_json", sa.Text()), sa.UniqueConstraint("project_id", "kind", "idempotency_key"))
    op.create_table("operation_tasks", sa.Column("task_id", sa.String(36), primary_key=True), sa.Column("operation_id", sa.String(36), sa.ForeignKey("operations.operation_id", ondelete="CASCADE"), nullable=False), sa.Column("unit_key", sa.String(128), nullable=False), sa.Column("provider_task_id", sa.String(128)), sa.Column("status", sa.String(24), nullable=False), sa.Column("submit_intent_at", sa.String(40)), sa.Column("last_polled_at", sa.String(40)), sa.Column("result_artifact_id", sa.String(36), sa.ForeignKey("artifacts.artifact_id")), sa.Column("error_json", sa.Text()), sa.UniqueConstraint("operation_id", "unit_key"))
    op.create_table("jobs", sa.Column("job_id", sa.String(36), primary_key=True), sa.Column("operation_id", sa.String(36), sa.ForeignKey("operations.operation_id")), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False), sa.Column("kind", sa.String(40), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("progress", sa.Integer(), nullable=False), sa.Column("heartbeat_at", sa.String(40)), sa.Column("created_at", sa.String(40), nullable=False), sa.Column("updated_at", sa.String(40), nullable=False))


def downgrade() -> None:
    for table in ("jobs", "operation_tasks", "operations", "motion_templates", "project_asset_bindings", "asset_versions", "rig_versions", "rigs", "assets", "authoring_reservations", "project_stage_heads", "artifacts", "projects", "channels"):
        op.drop_table(table)
