import argparse
from dataclasses import dataclass, field
from abc import abstractmethod, ABC
import subprocess
import bs4
import os.path
import os
import requests
import urllib.request
import tempfile
import magic
import zipfile
import stonpy
import libsbgnpy.utils

CD2SBGNML = os.path.realpath(os.path.join(os.path.dirname(__file__), "thirdparty/cd2sbgnml/cd2sbgnml.sh"))
REPOSITORIES = {
    "panther": ["http://data.pantherdb.org/ftp/pathway/3.6/CD4.1/"],
    "acsn_master": ["https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/ACSN_denovo_annotations.sbgn"],
    "acsn": [
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/adaptive_immune_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/angiogenesis_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/caf_cell_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/cellcycle_dnarepair_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/dendritic_cell_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/emt_senescence_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/innate_immune_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/invasion_motility_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/macrophages_mdsc_cells_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/natural_killer_cell_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/rcd_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/survival_master.sbgn",
        "https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/telomere_maintenance_master.sbgn"
    ],
    "recon": ["https://www.vmh.life/files/reconstructions/ReconMaps/ReconMap-2.01.zip"],
    "asthmamap": [
        "https://asthma-map.org/images/af/F002-AirwayEpithelialCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F015-AirwaySmoothMuscleCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F008-BCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F001-DendriticCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F011-Eosinophil-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F010-EosinophilPrecursor-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F014-Fibroblast-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F016-GobletCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F006-ILCPrecursor-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F007-ILC2-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F009-Macrophage-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F012-MastCell-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F013-Neutrophil-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F003-Th0-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F004-Th2-SBGNv02.sbgn",
        "https://asthma-map.org/images/af/F005-Treg-SBGNv02.sbgn",
        "https://asthma-map.org/images/pd/EicosanoidModule-0.0.42.xml",
        "https://asthma-map.org/images/pd/MastCellModule-0.0.40.xml"
    ]
}

class ConversionError(Exception):
    pass

@dataclass
class Target(ABC):
    path: str
    name: str

    @abstractmethod
    def make(self, ston: stonpy.core.STON) -> None:
        pass

@dataclass
class BatchTarget(Target):
    subtargets: list[Target] = field(default_factory=list, repr=False)

    def __post_init__(self):
        self.subtargets = self.prepare_subtargets()

    @abstractmethod
    def prepare_subtargets(self) -> list[Target]:
        pass

    def make(self, ston: stonpy.core.STON) -> None:
        for target in self.subtargets:
            make_target(target, ston)


@dataclass
class LocalFileTarget(Target):
    pass

@dataclass
class CellDesignerFileTarget(LocalFileTarget, BatchTarget):

    def prepare_subtargets(self):
        sbgnml_path = cd2sbgnml(self.path)
        if sbgnml_path is None:
            raise ConversionError("CellDesigner file could not be converted to SBGN-ML")
        subtarget = target_from_path(sbgnml_path, parent_target=self)
        return [subtarget]


@dataclass
class SBGNMLFileTarget(LocalFileTarget):

    def make(self, ston):
        create_map(self.path, ston, self.name)


@dataclass
class RepositoryTarget(BatchTarget):

    def prepare_subtargets(self):
        subtargets = []
        for subtarget_path in REPOSITORIES[self.path]:
            subtargets.append(
                target_from_path(subtarget_path, parent_target=self)
            )
        return subtargets

@dataclass
class LocalDirectoryTarget(BatchTarget):

    def prepare_subtargets(self):
        subtargets = []
        for subtarget_path in os.listdir(self.path):
            subtargets.append(
                target_from_path(
                    os.path.join(
                        self.path,
                        subtarget_path
                    ),
                    parent_target=self
                )
            )
        return subtargets

@dataclass
class RemoteFileTarget(BatchTarget):

    def prepare_subtargets(self):
        _, subtarget_path = tempfile.mkstemp()
        urllib.request.urlretrieve(self.path, subtarget_path)
        subtarget = target_from_path(subtarget_path, parent_target=self)
        return [subtarget]

@dataclass
class RemoteDirectoryTarget(BatchTarget):

    def prepare_subtargets(self):
        subtargets = []
        r = requests.get(self.path)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        urls = []
        for link in soup.find_all('a'):
            url = f"{self.path}{link.get('href')}"
            urls.append(url)
        for url in urls:
            try:
                target = target_from_path(url, self)
                subtargets.append(target)
            except ValueError:
                print("-> not a valid path")
            except ConversionError:
                print("-> could not be converted to SBGN-ML")
        return subtargets

@dataclass
class ZipFileTarget(BatchTarget):

    def prepare_subtargets(self):
        subtargets_path = tempfile.mkdtemp()
        with zipfile.ZipFile(self.path, "r") as zip_ref:
            zip_ref.extractall(subtargets_path)
        subtarget = target_from_path(subtargets_path, parent_target=self)
        return [subtarget]


def guess_target_type(target_path):
    if os.path.exists(target_path):
        if os.path.isfile(target_path):
            file_format = guess_file_format(target_path)
            if file_format == "text/sbgn-ml":
                return SBGNMLFileTarget
            elif file_format == "text/celldesigner":
                return CellDesignerFileTarget
            elif file_format == "application/zip":
                return ZipFileTarget
        elif os.path.isdir(target_path):
            return LocalDirectoryTarget
    elif target_path in REPOSITORIES:
        return RepositoryTarget
    else:
        headers = {"Range": "bytes=0-10"}
        r = requests.get(target_path, headers=headers)
        if r.ok:
            if target_path.endswith("/"):
                return RemoteDirectoryTarget
            else:
                return RemoteFileTarget
    return None


def guess_file_format(target_path):
    file_format = magic.from_file(filename=target_path, mime=True)
    if file_format == "text/xml":
        file_format = guess_pathway_file_format(target_path)
    return file_format


def guess_pathway_file_format(target_path):
    with open(target_path) as f:
        for line in f:
            if "<sbgn" in line:
                return "text/sbgn-ml"
            elif "<celldesigner" in line:
                return "text/celldesigner"
    return None


def target_name_from_path(target_path, parent_target=None):
    target_type = guess_target_type(target_path)
    if parent_target is None:
        return target_path
    if target_type is SBGNMLFileTarget:
        if isinstance(parent_target, LocalDirectoryTarget):
            return target_path
    return parent_target.path

def target_from_path(target_path, parent_target=None):
    if parent_target is None:
        print(f'* Preparing target from path {target_path}')
    else:
        print(f'* Preparing subtarget from path {target_path}')
        print(f'-> parent of target is {parent_target}')
    target_type = guess_target_type(target_path)
    if target_type is None:
        raise ValueError(f'could not find type of target at path "{target_path}"')
    print(f'-> type of target is {target_type.__name__}')
    target_name = target_name_from_path(target_path, parent_target=parent_target)
    print(f'-> name of target is {target_name}')
    if issubclass(target_type, BatchTarget):
        print(f'-> target has subtargets')
    target = target_type(
        target_path,
        target_name
    )
    return target


def make_target(target: Target, ston: stonpy.core.STON) -> None:
    print(f'* Making target {target}')
    target.make(ston)


def create_map(path, ston, map_id):
    print(f'-> creating map in database with id {map_id}')
    ston.create_map(path, map_id)

def cd2sbgnml(cd_path):
    _, sbgnml_path = tempfile.mkstemp()
    r = subprocess.run(
        [CD2SBGNML, cd_path, sbgnml_path],
        capture_output=True
    )
    if r.returncode != 0:
        print(r.stderr)
        return None
    return sbgnml_path

def list_repos():
    for repository in REPOSITORIES:
        print(repository)


def get_map(ston, map_id, sbgn_file=None):
    if sbgn_file is None:
        sbgn_map = ston.get_map(map_id)
        print(libsbgnpy.utils.write_to_string(sbgn_map[0]))
    else:
        ston.get_map_to_sbgn_file(map_id, sbgn_file)

def query(ston,
          query_string,
          output_file=None,
          convert=False,
          complete=False,
          merge_records=True,
          to_top_left=False,
          complete_process_modulations=False):
    if not convert:
        cursor = ston.graph.query(query_string)
        s = cursor.to_data_frame().to_string()
        if output_file is not None:
            with open(output_file, "w") as f:
                f.write(s)
        else:
            print(s)
    else:
        ston.query_to_sbgn_file(
            query=query_string,
            sbgn_file=output_file,
            complete=complete,
            merge_records=merge_records,
            to_top_left=to_top_left,
            complete_process_modulations=complete_process_modulations
        )

def delete_all(ston):
    print(f"Deleting all data of database")
    ston.graph.delete_all()


def run(args):
    if args.action == "list-repos":
        list_repos()
    elif args.action == "create" or \
            args.action == "get" or \
            args.action == "query" or \
            args.action == "delete-all":
        ston = stonpy.core.STON(
            uri=args.uri,
            user=args.user,
            password=args.password
        )
        if args.action == "create":
            if args.delete_all:
                delete_all(ston)
            print(f"Total of {len(args.target_paths)} targets")
            for target_path in args.target_paths:
                target = target_from_path(target_path)
                make_target(target, ston)
            print("Done.")
        elif args.action == "get":
            get_map(ston, args.map_id, args.output)
        elif args.action == "query":
            query(
                ston=ston,
                query_string=args.query_string,
                output_file=args.output,
                convert=args.convert,
                complete=args.complete,
                merge_records=not args.unmerge_records,
                to_top_left=args.to_top_left,
                complete_process_modulations=args.complete_process_modulations
            )
        elif args.action == "delete-all":
            delete_all(ston)

def main():
    parser = argparse.ArgumentParser(description="Tool for storing SBGN and CellDesigner maps in a Neo4j database, and query the database")
    subparsers = parser.add_subparsers(dest="action")
    list_repos_parser = subparsers.add_parser("list-repos", help="list the available map repositories")
    with_db_conn_parser = argparse.ArgumentParser(add_help=False)
    with_db_conn_parser.add_argument("-u", "--user", default=None, help="user name for accessing the database")
    with_db_conn_parser.add_argument("-a", "--uri", default=None, help="URI for accessing the database")
    with_db_conn_parser.add_argument("-p", "--password", default=None, help="password for accessing the database")
    delete_all_parser = subparsers.add_parser("delete-all", parents=[with_db_conn_parser])
    create_parser = subparsers.add_parser("create", parents=[with_db_conn_parser], help="create one or more maps in the database")
    create_parser.add_argument("-d", "--delete-all", default=False, action="store_true", help="delete all data in the database before executing the action")
    create_parser.add_argument("target_paths", nargs="+", help="target paths for the create command (SBGN-ML or CellDesigner file or URL, ZIP file, repository (see list-repos)")
    get_parser = subparsers.add_parser("get", parents=[with_db_conn_parser], help="get a map from the database using its id")
    get_parser.add_argument("-o", "--output", default=None, help="output SBGN-ML file where the map is written")
    get_parser.add_argument("map_id", help="the id of the map to get")
    query_parser = subparsers.add_parser("query", parents=[with_db_conn_parser], help="query the database")
    query_parser.add_argument("-o", "--output", default=None, help="output SBGN-ML file(s) where the result of the query is written (optional, result is printed to stdout if not set)")
    query_parser.add_argument("-c", "--convert", action="store_true", default=False, help="convert the result to SBGN-ML when possible")
    query_parser.add_argument("-k", "--complete", action="store_true", default=False, help="complete the converted result (only if --convert is set)")
    query_parser.add_argument("-m", "--unmerge-records", action="store_true", default=False, help="unmerge the records of the result (only if --convert is set)")
    query_parser.add_argument("-t", "--to-top-left", action="store_true", default=False, help="moves the ouput maps to the top left (only if --convert is set)")
    query_parser.add_argument("-n", "--complete-process-modulations", action="store_true", default=False, help="also completes processes with the modulations targeting them (only if --complete is set)")
    query_parser.add_argument("query_string", help="the cypher query")

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()
