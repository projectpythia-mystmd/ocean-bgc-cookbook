import os
import shutil
from glob import glob

import pathlib
import subprocess

import json
import yaml

import jupyter_client

from jinja2 import Template

import dask
from dask_jobqueue import PBSCluster
from dask.distributed import Client
import numpy as np
import xarray as xr

path_to_here = os.path.dirname(os.path.realpath(__file__))


def get_ClusterClient(memory="25GB", project="NCGD0011", on_hub=True):
    cluster = get_Cluster(memory, project, on_hub)
    client = Client(cluster)
    return cluster, client


def get_Cluster(memory="25GB", project="NCGD0011", on_hub=True):
    """return client and cluster"""
    USER = os.environ["USER"]

    cluster = PBSCluster(
        cores=1,
        memory=memory,
        processes=1,
        queue="casper",
        local_directory=f"/glade/scratch/{USER}/dask-workers",
        log_directory=f"/glade/scratch/{USER}/dask-workers",
        resource_spec=f"select=1:ncpus=1:mem={memory}",
        project=project,
        walltime="06:00:00"
    )

    if on_hub:
        jupyterhub_server_name = os.environ.get("JUPYTERHUB_SERVER_NAME", None)
        dashboard_link = (
            "https://jupyterhub.hpc.ucar.edu/stable/user/{USER}/proxy/{port}/status"
        )
        if jupyterhub_server_name:
            dashboard_link = (
                "https://jupyterhub.hpc.ucar.edu/stable/user/"
                + "{USER}"
                + f"/{jupyterhub_server_name}/proxy/"
                + "{port}/status"
            )
    else:
        dashboard_link = "http://localhost:8787/status"

    dask.config.set({"distributed.dashboard.link": dashboard_link})
    return cluster


class manage_conda_kernel(object):
    """Manage conda kernels so they can be see by `papermill`"""

    def __init__(self, kernel_name: str):
        self.kernel_name = kernel_name

    def getcwd(self):
        """get the directory of a conda kernel by name"""
        command = ["conda", "env", "list", "--json"]
        output = subprocess.check_output(command).decode("ascii")
        envs = json.loads(output)["envs"]

        for env in envs:
            env = pathlib.Path(env)
            if self.kernel_name == env.stem:
                return env
        else:
            return None

    def isinstalled(self):
        return self.kernel_name in jupyter_client.kernelspec.find_kernel_specs()

    def ensure_installed(self):
        """install a conda kernel in a location findable by `nbconvert` etc."""

        if self.isinstalled():
            return

        path = self.getcwd()
        if path is None:
            raise ValueError(f'conda kernel "{self.kernel_name}" not found')
        path = path / pathlib.Path("share/jupyter/kernels")

        kernels_in_conda_env = jupyter_client.kernelspec._list_kernels_in(path)
        py_kernel_key = [k for k in kernels_in_conda_env.keys() if "python" in k][0]
        kernel_path = kernels_in_conda_env[py_kernel_key]

        jupyter_client.kernelspec.install_kernel_spec(
            kernel_path, kernel_name=self.kernel_name, user=True, replace=True
        )
        assert self.isinstalled()


# class md_jinja_engine(NBClientEngine):
#     @classmethod
#     def execute_managed_notebook(cls, nb_man, kernel_name, **kwargs):
#         jinja_data = {} if "jinja_data" not in kwargs else kwargs["jinja_data"]

#         # call the papermill execution engine:
#         super().execute_managed_notebook(nb_man, kernel_name, **kwargs)

#         for cell in nb_man.nb.cells:
#             if cell.cell_type == "markdown":
#                 cell["source"] = Template(cell["source"]).render(**jinja_data)

def get_control_dict():
    with open("_config-calc.yml", "r") as fid:
        control = yaml.safe_load(fid)

    control["output_dir"] = f'{control["output_root"]}/{control["data_sources"]["casename"]}'
    os.makedirs(control["output_dir"], exist_ok=True)

    default_kernel_name = control.pop("default_kernel_name", None)

    if default_kernel_name is not None:
        for d in control["compute_notebooks"].values():
            if "kernel_name" not in d:
                d["kernel_name"] = default_kernel_name
    else:
        for nb, d in control["compute_notebooks"].items():
            assert "kernel_name" in d, f"kernel information missing for {nb}.ipynb"

    for nb, d in control["compute_notebooks"].items():
        manage_conda_kernel(d["kernel_name"]).ensure_installed()

    return control


def setup_book():
    """setup output jupyter book"""

    control = get_control_dict()

    # ensure directory
    output_dir = control["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    # write table of contents file
    toc = control["book_toc"]
    with open(f"{output_dir}/_toc.yml", "w") as fid:
        yaml.dump(toc, fid, sort_keys=False)

    # read config defaults
    with open(f"{path_to_here}/_jupyter-book-config-defaults.yml", "r") as fid:
        config = yaml.safe_load(fid)

    # update defaults
    config.update(control["book_config_keys"])

    # write config file
    with open(f"{output_dir}/_config.yml", "w") as fid:
        yaml.dump(config, fid, sort_keys=False)

    # check for files that are not computed
    # get list of computational notebooks
    compute_notebooks = [f"{f}.ipynb" for f in control["compute_notebooks"].keys()]

    # get toc files; ignore glob expressions
    toc_files = get_toc_files(toc, include_glob=False)
    copy_files = list(set(toc_files) - set(compute_notebooks))

    for src in copy_files:
        shutil.copyfile(src, f"{output_dir}/{src}")
        
    # TODO: check that all notebooks are in toc?
    #       requires resolving glob expression


def get_toc_files(toc_dict, include_glob=True):
    """return a list of files in the _toc.yml"""

    def _toc_files(toc_dict, file_list=[]):
        for key, value in toc_dict.items():
            if key in ["root", "file", "glob"]:
                if not include_glob and key == "glob":
                    continue
                file = (
                    glob(value)
                    if key == "glob"
                    else [
                        f"{value}.{ext}"
                        for ext in ["ipynb", "md"]
                        if os.path.exists(f"{value}.{ext}")
                    ]
                )

                assert len(file), f"no files found: {value}"
                assert len(file) == 1, f"multiple files found: {value}"
                file_list.append(file[0])

            elif key in ["chapters", "sections", "parts"]:
                file_list_ext = []
                for sub in value:
                    file_list_ext = _toc_files(sub, file_list_ext)
                file_list.extend(file_list_ext)

        return file_list

    return _toc_files(toc_dict)


def adjust_pop_grid(tlon,tlat,field):
    nj = tlon.shape[0]
    ni = tlon.shape[1]
    xL = int(ni/2 - 1)
    xR = int(xL + ni)

    tlon = np.where(np.greater_equal(tlon,min(tlon[:,0])),tlon-360.,tlon)
    lon  = np.concatenate((tlon,tlon+360.),1)
    lon = lon[:,xL:xR]

    if ni == 320:
        lon[367:-3,0] = lon[367:-3,0]+360.
    lon = lon - 360.
    lon = np.hstack((lon,lon[:,0:1]+360.))
    if ni == 320:
        lon[367:,-1] = lon[367:,-1] - 360.

    #-- trick cartopy into doing the right thing:
    #   it gets confused when the cyclic coords are identical
    lon[:,0] = lon[:,0]-1e-8
    
    #-- periodicity
    lat  = np.concatenate((tlat,tlat),1)
    lat = lat[:,xL:xR]
    lat = np.hstack((lat,lat[:,0:1]))

    field = np.ma.concatenate((field,field),1)
    field = field[:,xL:xR]
    field = np.ma.hstack((field,field[:,0:1]))
    return lon,lat,field


def global_mean(ds, ds_grid, compute_vars, normalize=True, include_ms=False):
    """
    Compute the global mean on a POP dataset. 
    Return computed quantity in conventional units.
    """

    other_vars = list(set(ds.variables) - set(compute_vars))

    if include_ms: # marginal seas!
        surface_mask = ds_grid.TAREA.where(ds_grid.KMT > 0).fillna(0.)
    else:
        surface_mask = ds_grid.TAREA.where(ds_grid.REGION_MASK > 0).fillna(0.)        
    
    masked_area = {
        v: surface_mask.where(ds[v].notnull()).fillna(0.) 
        for v in compute_vars
    }
    
    with xr.set_options(keep_attrs=True):
        
        dso = xr.Dataset({
            v: (ds[v] * masked_area[v]).sum(['nlat', 'nlon'])
            for v in compute_vars
        })
        
        if normalize:
            dso = xr.Dataset({
                v: dso[v] / masked_area[v].sum(['nlat', 'nlon'])
                for v in compute_vars
            })            
                
    return dso
