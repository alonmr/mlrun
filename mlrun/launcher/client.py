# Copyright 2023 MLRun Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import abc
import getpass
import os

import IPython

import mlrun.errors
import mlrun.launcher.base
import mlrun.lists
import mlrun.model
import mlrun.runtimes
from mlrun.utils import logger


class ClientBaseLauncher(mlrun.launcher.base.BaseLauncher, abc.ABC):
    """
    Abstract class for common code between client launchers
    """

    @staticmethod
    def _enrich_runtime(runtime):
        runtime.try_auto_mount_based_on_config()
        runtime._fill_credentials()

    def _store_function(
        self, runtime: "mlrun.runtimes.BaseRuntime", run: "mlrun.run.RunObject"
    ):
        run.metadata.labels["kind"] = runtime.kind
        if "owner" not in run.metadata.labels:
            run.metadata.labels["owner"] = (
                os.environ.get("V3IO_USERNAME") or getpass.getuser()
            )
        if run.spec.output_path:
            run.spec.output_path = run.spec.output_path.replace(
                "{{run.user}}", run.metadata.labels["owner"]
            )

        if self.db and runtime.kind != "handler":
            struct = runtime.to_dict()
            hash_key = self.db.store_function(
                struct, runtime.metadata.name, runtime.metadata.project, versioned=True
            )
            run.spec.function = runtime._function_uri(hash_key=hash_key)

    def _refresh_function_metadata(self, runtime: "mlrun.runtimes.BaseRuntime"):
        try:
            meta = runtime.metadata
            db_func = self.db.get_function(meta.name, meta.project, meta.tag)
            if db_func and "status" in db_func:
                runtime.status = db_func["status"]
                if (
                    runtime.status.state
                    and runtime.status.state == "ready"
                    and runtime.kind
                    # We don't want to override the nuclio image here because the build happens in nuclio
                    # TODO: have a better way to check if nuclio function deploy started
                    and not hasattr(runtime.status, "nuclio_name")
                ):
                    runtime.spec.image = mlrun.utils.get_in(
                        db_func, "spec.image", runtime.spec.image
                    )
        except mlrun.errors.MLRunNotFoundError:
            pass

    @staticmethod
    def _log_track_results(
        runtime: "mlrun.runtimes.BaseRuntime", result: dict, run: "mlrun.run.RunObject"
    ):
        """
        log commands to track results
        in jupyter, displays a table widget with the result
        else, logs CLI commands to track results and a link to the results in UI

        :param: runtime: runtime object
        :param result:   run result dict
        :param run:      run object
        """
        uid = run.metadata.uid
        project = run.metadata.project

        # show ipython/jupyter result table widget
        results_tbl = mlrun.lists.RunList()
        if result:
            results_tbl.append(result)
        else:
            logger.info("no returned result (job may still be in progress)")
            results_tbl.append(run.to_dict())

        if mlrun.utils.is_ipython and mlrun.config.ipython_widget:
            results_tbl.show()
            print()
            ui_url = mlrun.utils.get_ui_url(project, uid)
            if ui_url:
                ui_url = f' or <a href="{ui_url}" target="_blank">click here</a> to open in UI'
            IPython.display.display(
                IPython.display.HTML(
                    f"<b> > to track results use the .show() or .logs() methods {ui_url}</b>"
                )
            )
        elif not runtime.is_child:
            project_flag = f"-p {project}" if project else ""
            info_cmd = f"mlrun get run {uid} {project_flag}"
            logs_cmd = f"mlrun logs {uid} {project_flag}"
            logger.info(
                "To track results use the CLI", info_cmd=info_cmd, logs_cmd=logs_cmd
            )
            ui_url = mlrun.utils.get_ui_url(project, uid)
            if ui_url:
                logger.info("Or click for UI", ui_url=ui_url)
