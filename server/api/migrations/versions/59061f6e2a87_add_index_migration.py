# Copyright 2023 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""add index migration

Revision ID: 59061f6e2a87
Revises: 27ed4ecb734c
Create Date: 2023-11-05 12:43:53.787957

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "59061f6e2a87"
down_revision = "27ed4ecb734c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("idx_runs_project_id", "runs", ["id", "project"], unique=True)

    op.create_index(
        "idx_artifacts_labels_name_value",
        "artifacts_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_entities_labels_name_value",
        "entities_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_feature_sets_labels_name_value",
        "feature_sets_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_projects_labels_name_value",
        "projects_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_functions_labels_name_value",
        "functions_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_features_labels_name_value",
        "features_labels",
        ["name", "value"],
        unique=False,
    )
    op.create_index(
        "idx_feature_vectors_labels_name_value",
        "feature_vectors_labels",
        ["name", "value"],
        unique=False,
    )

    op.create_index(
        "idx_runs_labels_name_value", "runs_labels", ["name", "value"], unique=False
    )

    op.create_index(
        "idx_schedules_v2_labels_name_value",
        "schedules_v2_labels",
        ["name", "value"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_runs_project_id", table_name="runs")
    op.drop_index(
        "idx_schedules_v2_labels_name_value", table_name="schedules_v2_labels"
    )
    op.drop_index("idx_runs_labels_name_value", table_name="runs_labels")
    op.drop_index("idx_projects_labels_name_value", table_name="projects_labels")
    op.drop_index("idx_functions_labels_name_value", table_name="functions_labels")
    op.drop_index("idx_features_labels_name_value", table_name="features_labels")
    op.drop_index(
        "idx_feature_vectors_labels_name_value", table_name="feature_vectors_labels"
    )
    op.drop_index(
        "idx_feature_sets_labels_name_value", table_name="feature_sets_labels"
    )
    op.drop_index("idx_entities_labels_name_value", table_name="entities_labels")
    op.drop_index("idx_artifacts_labels_name_value", table_name="artifacts_labels")
    # ### end Alembic commands ###