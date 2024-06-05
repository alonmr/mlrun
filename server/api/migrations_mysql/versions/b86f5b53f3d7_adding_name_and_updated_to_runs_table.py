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
"""Adding name and updated to runs table

Revision ID: b86f5b53f3d7
Revises: 4903aef6a91d
Create Date: 2022-01-08 19:28:45.141873

"""

import datetime

import sqlalchemy as sa
from alembic import op

import server.api.utils.db.sql_collation

# revision identifiers, used by Alembic.
revision = "b86f5b53f3d7"
down_revision = "4903aef6a91d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "runs",
        sa.Column(
            "name",
            sa.String(
                length=255,
                collation=server.api.utils.db.sql_collation.SQLCollationUtil.collation(),
            ),
            default="no-name",
        ),
    )
    op.add_column(
        "runs", sa.Column("updated", sa.TIMESTAMP(), default=datetime.datetime.utcnow)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("runs", "updated")
    op.drop_column("runs", "name")
    # ### end Alembic commands ###