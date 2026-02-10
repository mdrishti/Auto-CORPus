"""Module to run the autocorpus pipeline."""

from pathlib import Path

from . import logger
from .file_processing import process_file


def run_autocorpus(config, structure, key, output_format):
    """Run the autocorpus pipeline on a given file.

    Args:
        config: The configuration file to use.
        structure: The structure of the input files.
        key: The key in the structure dict for the current file.
        output_format: The output format to use (JSON or XML).
    """
    logger.info("Sending files for processing...")
    ac = process_file(
        config=config,
        file_path=Path(structure[key]["main_text"]),
        linked_tables=sorted(Path(lt) for lt in structure[key]["linked_tables"]),
    )
    # logger.info(f"ac:{ac}")
    logger.info("Sent for processing...")

    out_dir = Path(structure[key]["out_dir"])
    key = key.replace("\\", "/")

    # Only write main_text files if there's actual main text content
    if structure[key]["main_text"] and ac.main_text:
        try:
            if output_format.lower() == "json":
                logger.info("ac:main_text_to_bioc")
                with open(
                    out_dir / f"{Path(key).name}_bioc.json",
                    "w",
                    encoding="utf-8",
                ) as outfp:
                    outfp.write(ac.main_text_to_bioc_json())
            else:
                with open(
                    out_dir / f"{Path(key).name}_bioc.xml",
                    "w",
                    encoding="utf-8",
                ) as outfp:
                    outfp.write(ac.main_text_to_bioc_xml())
            with open(
                out_dir / f"{Path(key).name}_abbreviations.json",
                "w",
                encoding="utf-8",
            ) as outfp:
                outfp.write(ac.abbreviations_to_bioc_json())
        except Exception as e:
            logger.warning(
                f"Failed to convert main_text to BioC format for {key}: {e}. "
                "Skipping main_text output, but will still process tables if available."
            )

        ## TODO: Uncomment when SI conversion is supported
        # out_filename = str(file_path).replace(".pdf", ".pdf_bioc.json")
        # with open(out_filename, "w", encoding="utf-8") as f:
        #     BioCJSON.dump(bioc_text, f, indent=4)

        # out_table_filename = str(file_path).replace(".pdf", ".pdf_tables.json")
        # with open(out_table_filename, "w", encoding="utf-8") as f:
        #     BioCTableJSON.dump(bioc_tables, f, indent=4)

    # AC does not support the conversion of tables or abbreviations to XML
    if ac.has_tables:
        with open(
            out_dir / f"{Path(key).name}_tables.json", "w", encoding="utf-8"
        ) as outfp:
            outfp.write(ac.tables_to_bioc_json())
