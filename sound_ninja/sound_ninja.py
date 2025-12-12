from pathlib import Path
import commentjson
import sys
import os
from typing import Dict, List, Tuple, Optional, Any, Literal
from reticulator import *

PackType = Literal['data', 'resource']

DEFAULT_FORMAT_VERSION: str = "1.21.40"
BP_DEFAULT_PATH: str = "./BP"
RP_DEFAULT_PATH: str = "./RP"

def get_block_tuples(BP: BehaviorPack, debug: bool, default: Optional[str]) -> List[Tuple[str, str]]:
    """
    Extracts block identifiers and their associated sounds from all JSON files in the given behavior pack.

    Args:
        BP (Path): Path to the behavior pack containing block JSON files.

    Returns:
        List[Tuple[str, str]]: A list of tuples, each containing a block identifier and its corresponding sound type.
    """
    block_tuples: List[Tuple[str, str]] = []
    for block in BP.blocks:
        # ignore the file if it's not a valid JSON
        try:
            identifier = block.identifier
        except reticulator.AssetNotFoundError:
            print(f"Warning: {block.filepath} has no identifier, skipping...")
            continue

        try:
            sound: Optional[str] = block.pop_jsonpath("minecraft:block/description/sound")
            block_tuples.append((identifier, sound))
        except reticulator.AssetNotFoundError:
            if debug: print(f"WARNING: {identifier} has no sound reference in description ({block.filepath})")
            if default is not None: block_tuples.append((identifier, default))
        block.save()
            
    return block_tuples


def update_block_sounds(block_sounds_path: Path, block_tuples: List[Tuple[str, str]], format_version: Optional[str]) -> None:
    """
    Updates sound definitions for blocks inside blocks.json file.

    This function loads the blocks.json structure (creating a minimal one if needed),
    then applies the sound values provided in `block_tuples`. Existing entries are
    updated, and missing entries are created. The resulting structure is then written
    back to disk.

    Args:
        block_sounds_path (Path): path to the blocks.json file to update.
        block_tuples (List[Tuple[str, str]]): a list of (identifier, sound) pairs
                                              extracted from block definitions.
        settings (Dict[str, Any]): settings dictionary containing at least the
                                   optional "formatVersion" key for initialization.

    Raises:
        SystemExit: if the file cannot be written to disk.
    """
    
    block_sounds = load_blocksjson(block_sounds_path, format_version)
    for identifier, sound in block_tuples:
        if identifier in block_sounds:
            block_sounds[identifier]['sound'] = sound
        else:
            block_sounds[identifier] = { "sound": sound }
    
    try:
        with open(block_sounds_path, 'w', encoding='utf-8') as fw:
            fw.write(commentjson.dumps(block_sounds, indent=4))
    except Exception as e:
        print(f"Error writing {block_sounds_path}: {e}")
        raise SystemExit
def load_blocksjson(block_sounds_path: Path, format_version: Optional[str]) -> Dict[str, Any]:
    """
    Ensures that the blocks.json file exists and returns its JSON content.

    - If the file does not exist, a new JSON structure is created with a valid
    `format_version`.
    - If `format_version` is not provided in filter settings, the default value
    defined by `DEFAULT_FORMAT_VERSION` is used.

    If the file exists, its content is loaded and returned.

    Args:
        block_sounds_path (Path): path to the blocks.json file.
        format_version (Optional[str]): explicit format version to use when creating
                                        the file. If None, the default version is used.

    Returns:
        Dict[str, Any]: the JSON content of the existing file, or a newly generated
                        JSON structure containing at least a `format_version` key.
    """
    if not block_sounds_path.is_file():
        print("Missing blocks.json file, creating one...")

        final_version = format_version or DEFAULT_FORMAT_VERSION
        if format_version is None:
            print(f"No \"formatVersion\" provided for blocks.json, using default ({DEFAULT_FORMAT_VERSION})")
        return { "format_version": final_version }
    
    return commentjson.load(open(block_sounds_path, 'r', encoding='utf-8'))


def validate_pack(pack: Pack, expected_key: PackType) -> None:
    """
    Validates that the given pack contains a valid manifest.json file and that its type
    matches the expected value.

    This function checks that:
      - the manifest.json file exists in the pack directory,
      - the file contains at least one module,
      - the type of the first module matches `expected_key`.

    If any of these checks fail, the program exits with SystemExit.

    Args:
        pack (Pack): the pack (BehaviorPack or ResourcePack) to validate
        expected_key (str): the expected module type ("behaviorPack" or "resourcePack")

    Raises:
        SystemExit: if manifest.json is missing, empty, or the module type does not match.
    """
    pack_path = Path(pack.input_path).resolve()
    manifest_path = pack_path / "manifest.json"

    if not manifest_path.exists():
        print(f"Error: No manifest found in {Path(pack.input_path)}")
        raise SystemExit
    
    with open(manifest_path, "r", encoding='utf-8') as fr:
        manifest_json = commentjson.load(fr)
    modules = manifest_json.get("modules", [])
    if not modules:
        print(f"Error: manifest in {Path(pack.input_path)} not found or invalid")
        raise SystemExit

    pack_type = modules[0].get("type")
    if pack_type != expected_key:
        print(f"Error: manifest in {Path(pack.input_path)} not found or invalid")
        raise SystemExit
def initProject(settings: Dict[str, Any]) -> Project:
    """
    Initializes a Minecraft project by loading the Behavior Pack and Resource Pack,
    validating their manifests.
    
    Return:
      Project: current project.

    Raises:
        SystemExit: if any validation fail
    """

    BP_path = settings.get("behaviorPack")
    if BP_path is None:
        print(f"No parameter provided for behaviorPack, using default ({BP_DEFAULT_PATH})")
        BP_path = BP_DEFAULT_PATH
    RP_path = settings.get("resourcePack")
    if RP_path is None:
        print(f"No parameter provided for resourcePack, using default ({RP_DEFAULT_PATH})")
        RP_path = RP_DEFAULT_PATH
    project = Project(BP_path , RP_path)
    validate_pack(project.behavior_pack, 'data')
    validate_pack(project.resource_pack, 'resources')

    return project

def getSettings() -> Dict[str, Any]:
    """
    Returns the settings parsed from the first command-line argument as JSON,
    or an empty dictionary if no argument is provided.

    Raises:
        SystemExit: if the provided JSON is invalid.
    """
    if len(sys.argv) > 1:
        try:
            return commentjson.loads(sys.argv[1])
        except commentjson.JSONLibraryException as e:
            print(f"Error parsing settings JSON: {e}")
            raise SystemExit
    else:
        return {}

def main():
    settings: List[str, Any] = getSettings()
    project: Project = initProject(settings)
    
    block_tuples: List[Tuple[str, str]] = get_block_tuples(
        project.behavior_pack,
        settings.get("debug", False),
        settings.get("default", None)
    )
            
    update_block_sounds(
        Path(project.resource_pack.input_path).resolve() / "blocks.json",
        block_tuples,
        settings.get("formatVersion")
    )

if __name__ == "__main__":
    main()