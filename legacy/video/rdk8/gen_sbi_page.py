"""RDKE southbound API list generator."""
from build import build_api
from import_apis import convert_excel_to_json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_southbound() -> None:
    convert_excel_to_json(
        ROOT / "RDK8-southbound-api-spec.xlsx",
        ROOT / "southbound-apis.json",
        {
            "halInterface": ("hal interface", "interface", "header", "api"),
            "source": ("source", "reference", "url"),
            "type": ("type",),
            "releaseTag": ("release/tag version", "release", "tag", "version"),
        },
    )
    build_api(
        data_file="southbound-apis.json",
        output_file="southbound-api-spec.html",
        active="southbound",
        title="Southbound API Specifications",
        description="The Hardware Abstraction Layer (HAL) between middleware and the vendor layer — standardized interfaces that abstract hardware differences.",
        columns=["HAL interface", "Version", "Source"],
        fields=["halInterface", "releaseTag", "source"],
        link_field="source",
        search_placeholder="Search Southbound APIs",
        empty_message="No Southbound APIs have been loaded.",
        sort_field="halInterface",
        strip_release_path=True,
        show_version=False,
        hero_status="Published",
    )

if __name__ == "__main__":
    build_southbound()
